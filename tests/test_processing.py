"""Tests for the spatial and temporal processing chain."""

import geopandas as gpd
import numpy as np
import pytest
import xarray as xr
from conftest import make_store

from ewatercycle_destine.processing import (
    clip_to_shape,
    crop_time,
    crop_to_bbox,
    spatial_mean,
    to_daily,
)
from ewatercycle_destine.store import to_cmor_names

RHINE_BOUNDS = (4.15, 46.32, 11.87, 52.15)


def test_crop_time():
    ds = make_store(days=3)
    cropped = crop_time(ds, "2000-01-02T00:00:00Z", "2000-01-02T23:00:00Z")
    assert cropped.sizes["time"] == 24
    assert str(cropped["time"][0].to_numpy())[:10] == "2000-01-02"


def test_crop_time_rejects_non_utc():
    ds = make_store()
    with pytest.raises(ValueError, match="not in UTC"):
        crop_time(ds, "2000-01-01", "2000-01-02")


@pytest.mark.parametrize("descending", [True, False])
def test_crop_to_bbox_covers_the_catchment(descending):
    ds = to_cmor_names(make_store(descending_latitude=descending))
    cropped = crop_to_bbox(ds, RHINE_BOUNDS)

    latitudes = cropped["lat"].to_numpy()
    longitudes = cropped["lon"].to_numpy()
    assert latitudes.size > 0
    assert latitudes.min() <= RHINE_BOUNDS[1]
    assert latitudes.max() >= RHINE_BOUNDS[3]
    assert longitudes.min() <= RHINE_BOUNDS[0]
    assert longitudes.max() >= RHINE_BOUNDS[2]
    # The subset is smaller than the store it came from.
    assert cropped.sizes["lat"] < ds.sizes["lat"]


def test_crop_to_bbox_keeps_the_stores_latitude_order():
    descending = crop_to_bbox(to_cmor_names(make_store(descending_latitude=True)), RHINE_BOUNDS)
    ascending = crop_to_bbox(to_cmor_names(make_store(descending_latitude=False)), RHINE_BOUNDS)

    assert descending["lat"][0] > descending["lat"][-1]
    assert ascending["lat"][0] < ascending["lat"][-1]
    np.testing.assert_allclose(
        descending["lat"].to_numpy()[::-1], ascending["lat"].to_numpy()
    )


def test_crop_to_bbox_pads_by_a_grid_cell():
    # A "catchment" far smaller than a grid cell, between two coordinates.
    ds = make_store(resolution=0.5)
    cropped = crop_to_bbox(to_cmor_names(ds), (5.6, 50.6, 5.65, 50.65))
    assert cropped.sizes["lat"] > 0
    assert cropped.sizes["lon"] > 0


def test_crop_to_bbox_rejects_0_360_longitudes():
    ds = make_store()
    ds = ds.assign_coords(longitude=ds["longitude"] + 180.0)
    with pytest.raises(ValueError, match=r"-180\.\.180"):
        crop_to_bbox(to_cmor_names(ds), RHINE_BOUNDS)


def test_spatial_mean_weights_by_cos_latitude():
    # Two rows: 60 degrees north (weight cos(60) = 0.5) and the equator
    # (weight 1). Their unweighted mean is 2.0, the weighted one is not.
    ds = xr.Dataset(
        {"tas": (("lat", "lon"), [[1.0], [3.0]])},
        coords={"lat": [60.0, 0.0], "lon": [5.0]},
    )
    expected = (np.cos(np.deg2rad(60.0)) * 1.0 + 1.0 * 3.0) / (
        np.cos(np.deg2rad(60.0)) + 1.0
    )

    result = float(spatial_mean(ds)["tas"])

    assert result == pytest.approx(expected)
    assert result == pytest.approx(2.3333333, abs=1e-6)
    assert result != pytest.approx(2.0)  # what an unweighted mean would give


def test_spatial_mean_ignores_cells_outside_the_catchment():
    # Clipping leaves NaN outside the outline; those must not drag the mean
    # down, nor keep their share of the weight.
    ds = xr.Dataset(
        {"tas": (("lat", "lon"), [[np.nan], [3.0]])},
        coords={"lat": [60.0, 0.0], "lon": [5.0]},
    )
    assert float(spatial_mean(ds)["tas"]) == pytest.approx(3.0)


def test_clip_to_shape(rhine):
    gdf = gpd.read_file(rhine).to_crs("EPSG:4326")
    ds = crop_to_bbox(to_cmor_names(make_store(days=1)), tuple(gdf.total_bounds))

    clipped = clip_to_shape(ds, gdf)

    # Cells inside the catchment keep their value, cells outside are NaN.
    tas = clipped["tas"].isel(time=0)
    assert bool(tas.notnull().any())
    assert bool(tas.isnull().any())


def test_clip_to_shape_keeps_sub_cell_catchments(rhine):
    # A catchment smaller than one grid cell: without all_touched=True this
    # comes back empty.
    gdf = gpd.read_file(rhine).to_crs("EPSG:4326")
    tiny = gpd.GeoDataFrame(geometry=[gdf.geometry.iloc[0].centroid.buffer(0.01)], crs=gdf.crs)
    ds = crop_to_bbox(
        to_cmor_names(make_store(days=1, resolution=2.0)), tuple(tiny.total_bounds)
    )

    clipped = clip_to_shape(ds, tiny)

    assert bool(clipped["tas"].notnull().any())


def test_to_daily():
    ds = make_store(days=3)
    daily = to_daily(ds)
    assert daily.sizes["time"] == 3
