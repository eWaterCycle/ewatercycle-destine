"""Turning a global hourly store into catchment forcing.

Cut down to the catchment's bounding box, clip to its outline, reduce space,
then aggregate to daily. Space is reduced before time on purpose: the result is
identical and there is far less data to resample.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import rioxarray  # noqa: F401  # registers the .rio accessor on xarray objects
import xarray as xr
from ewatercycle.util import get_time

from ewatercycle_destine.store import LAT, LON


def crop_time(ds: xr.Dataset, start_time: str, end_time: str) -> xr.Dataset:
    """Select the requested period from a dataset.

    Args:
        ds: Dataset with a ``time`` dimension.
        start_time: Start of the period, as 'YYYY-MM-DDTHH:MM:SSZ'.
        end_time: End of the period, as 'YYYY-MM-DDTHH:MM:SSZ'.

    Returns:
        The dataset, limited to the period.
    """
    start = pd.Timestamp(get_time(start_time)).tz_convert(None)
    end = pd.Timestamp(get_time(end_time)).tz_convert(None)
    return ds.sel(time=slice(start, end))


def crop_to_bbox(
    ds: xr.Dataset, bounds: tuple[float, float, float, float]
) -> xr.Dataset:
    """Subset a global dataset to a bounding box, padded by one grid cell.

    Clipping to a polygon loads the cells it touches, so the global store has
    to be cut down to the catchment first. The padding keeps catchments that
    are smaller than a grid cell from falling between the coordinates.

    Args:
        ds: Dataset on a regular lat/lon grid.
        bounds: (minx, miny, maxx, maxy), as returned by
            :py:attr:`geopandas.GeoDataFrame.total_bounds`.

    Returns:
        The dataset, limited to the bounding box.

    Raises:
        ValueError: If the store's longitudes are not on a -180..180 grid, in
            which case slicing by the shapefile's bounds would be wrong.
    """
    minx, miny, maxx, maxy = bounds
    lon, lat = ds[LON], ds[LAT]

    if float(lon.max()) > 180.0:
        msg = (
            f"Expected longitudes on a -180..180 grid, but the store runs up to "
            f"{float(lon.max())}. Convert the store's longitudes before subsetting."
        )
        raise ValueError(msg)

    pad_lon, pad_lat = _grid_spacing(lon), _grid_spacing(lat)
    lat_slice = slice(miny - pad_lat, maxy + pad_lat)
    if lat.size > 1 and float(lat[0]) > float(lat[-1]):  # descending latitude
        lat_slice = slice(maxy + pad_lat, miny - pad_lat)

    return ds.sel({LON: slice(minx - pad_lon, maxx + pad_lon), LAT: lat_slice})


def _grid_spacing(coord: xr.DataArray) -> float:
    """Return the largest step between successive coordinate values."""
    if coord.size < 2:
        return 0.0
    return float(np.abs(np.diff(coord.to_numpy())).max())


def clip_to_shape(ds: xr.Dataset, gdf: gpd.GeoDataFrame) -> xr.Dataset:
    """Clip a dataset to the catchment outline.

    Args:
        ds: Dataset on a regular lat/lon grid, already cut down to roughly the
            catchment's bounding box.
        gdf: The catchment.

    Returns:
        The dataset, with cells outside the catchment set to NaN and fully
        outside rows and columns dropped.
    """
    ds = ds.rio.write_crs("EPSG:4326").rio.set_spatial_dims(x_dim=LON, y_dim=LAT)
    # all_touched keeps catchments smaller than a grid cell from coming back empty.
    return ds.rio.clip(gdf.geometry, gdf.crs, all_touched=True, drop=True)


def spatial_mean(ds: xr.Dataset) -> xr.Dataset:
    """Average over the catchment, weighting cells by their area.

    Grid cells of a regular lat/lon grid shrink towards the poles with the
    cosine of the latitude; an unweighted mean over-weights the northern cells
    of a catchment.

    Args:
        ds: Dataset on a regular lat/lon grid, clipped to the catchment.

    Returns:
        The dataset with the two spatial dimensions reduced away.
    """
    weights = np.cos(np.deg2rad(ds[LAT]))
    return ds.weighted(weights).mean(dim=(LAT, LON))


def to_daily(ds: xr.Dataset) -> xr.Dataset:
    """Aggregate hourly data to daily means.

    All variables are instantaneous values or time-mean rates, so the daily
    mean is the right aggregation for each of them.

    Args:
        ds: Dataset with an hourly ``time`` dimension.

    Returns:
        The dataset, resampled to daily means.
    """
    return ds.resample(time="1D").mean()
