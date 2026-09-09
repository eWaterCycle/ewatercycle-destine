"""Forcing from the DestinE Climate DT, served as zarr by the Earth Data Hub.

Access needs a DestinE Earth Data Hub API key, see
:py:mod:`ewatercycle_destine.auth`. Which model, experiment and variant are on
offer is described in :py:mod:`ewatercycle_destine.store`.
"""

from pathlib import Path
from typing import ClassVar

import geopandas as gpd
from ewatercycle._forcings.makkink import LumpedMakkinkForcing, et_makkink
from ewatercycle.base.forcing import DefaultForcing
from ewatercycle.util import get_time

from ewatercycle_destine.processing import (
    clip_to_shape,
    crop_time,
    crop_to_bbox,
    spatial_mean,
    to_daily,
)
from ewatercycle_destine.store import (
    ATTRIBUTES,
    DEFAULT_VARIABLES,
    STORE_NAMES,
    open_store,
    resolve_variables,
    to_cmor_names,
)


class DestinEForcing(DefaultForcing):
    """Distributed forcing from the DestinE Climate DT, via the Earth Data Hub.

    Examples:
        Gridded forcing for the Rhine over 2000, from the historical run:

        .. code-block:: python

            from pathlib import Path
            from ewatercycle.forcing import sources

            forcing = sources["DestinEForcing"].generate(
                start_time="2000-01-01T00:00:00Z",
                end_time="2000-12-31T00:00:00Z",
                directory="./destine_rhine",
                shape=Path("Rhine.shp"),
                experiment="hist",
            )

        which gives something like:

        .. code-block:: python

            DestinEForcing(
                start_time='2000-01-01T00:00:00Z',
                end_time='2000-12-31T00:00:00Z',
                directory=PosixPath('/home/mark/destine_rhine'),
                shape=PosixPath('/home/mark/destine_rhine/Rhine.shp'),
                filenames={
                    'pr': 'DestinE_IFS-FESOM_hist_standard_day_pr_2000-01-01_2000-12-31.nc',
                    'tas': 'DestinE_IFS-FESOM_hist_standard_day_tas_2000-01-01_2000-12-31.nc',
                    'rsds': 'DestinE_IFS-FESOM_hist_standard_day_rsds_2000-01-01_2000-12-31.nc',
                    'evspsblpot': 'DestinE_IFS-FESOM_hist_standard_day_evspsblpot_2000-01-01_2000-12-31.nc'
                }
            )
    """  # noqa: E501

    lumped: ClassVar[bool] = False

    @classmethod
    def generate(  # type: ignore[override]
        cls,
        start_time: str,
        end_time: str,
        directory: str | Path,
        shape: str | Path,
        variables: tuple[str, ...] = DEFAULT_VARIABLES,
        model: str = "IFS-FESOM",
        experiment: str = "hist",
        variant: str = "standard",
        **kwargs,  # noqa: ARG003
    ) -> "DestinEForcing":
        """Retrieve DestinE Climate DT forcing for a catchment.

        Args:
            start_time: Start time of forcing in UTC and ISO format string e.g.
                'YYYY-MM-DDTHH:MM:SSZ'.
            end_time: End time of forcing in UTC and ISO format string e.g.
                'YYYY-MM-DDTHH:MM:SSZ'.
            directory: Directory in which forcing should be written.
            shape: Path to a shape file. Used for spatial selection.
            variables: Variables to write, in CMOR names. ``evspsblpot`` is
                derived here with the Makkink equation, the rest is read from
                the store.
            model: Climate model, one of :py:data:`MODELS`.
            experiment: Experiment, one of :py:data:`EXPERIMENTS`.
            variant: Store variant, one of :py:data:`VARIANTS`. Only
                ``standard`` carries radiation.
            **kwargs: Ignored, for compatibility with the base class.

        Returns:
            The generated forcing, already saved to ``directory``.

        Raises:
            ValueError: If a variable is unknown, or the variant cannot supply
                it.
        """
        needed = resolve_variables(variables, variant)
        gdf = gpd.read_file(shape).to_crs("EPSG:4326")

        ds = open_store(model, experiment, variant)
        ds = ds[[STORE_NAMES[variable] for variable in sorted(needed)]]
        ds = to_cmor_names(ds)
        ds = crop_time(ds, start_time, end_time)
        ds = crop_to_bbox(ds, tuple(gdf.total_bounds))
        ds = clip_to_shape(ds, gdf)

        # Reduce space before time: same result, far less data to resample.
        if cls.lumped:
            centroid = gdf.geometry.union_all().centroid
            ds = spatial_mean(ds).assign_coords(lat=centroid.y, lon=centroid.x)
        ds = to_daily(ds).compute()

        for variable in ds.data_vars:
            ds[variable].attrs = dict(ATTRIBUTES[str(variable)])
        if "evspsblpot" in variables:
            ds["evspsblpot"] = et_makkink(ds["tas"], ds["rsds"])

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        period = f"{get_time(start_time):%Y-%m-%d}_{get_time(end_time):%Y-%m-%d}"
        prefix = f"DestinE_{model}_{experiment}_{variant}_day"

        # Basenames, not paths: DefaultForcing joins them onto self.directory,
        # which is what makes the forcing directory movable.
        filenames = {
            variable: f"{prefix}_{variable}_{period}.nc" for variable in variables
        }
        # spatial_ref is rioxarray's bookkeeping, not part of the forcing.
        ds = ds.drop_vars("spatial_ref", errors="ignore")
        for variable, filename in filenames.items():
            ds[variable].to_netcdf(directory / filename)

        forcing = cls(
            directory=directory,
            start_time=start_time,
            end_time=end_time,
            shape=Path(shape),
            filenames=filenames,
        )
        forcing.save()
        # save() copies the shapefile into the directory; point at that copy so
        # the object matches what load() returns and the directory stands alone.
        if forcing.shape is not None and not forcing.shape.is_relative_to(directory):
            forcing.shape = directory / forcing.shape.name
        return forcing


# Both bases declare generate(); ours wins the MRO, which is the point.
class DestinELumpedMakkinkForcing(DestinEForcing, LumpedMakkinkForcing):  # type: ignore[misc]
    """Catchment-averaged forcing from the DestinE Climate DT.

    Identical to :py:class:`DestinEForcing`, except that the grid is reduced to
    a single area-weighted catchment average, as lumped models expect.

    It also *is* a
    :py:class:`~ewatercycle._forcings.makkink.LumpedMakkinkForcing`: the
    variables and the Makkink potential evaporation are the same, only the
    source differs. Models annotate their forcing field with that type -- HBV,
    for one, accepts ``LumpedMakkinkForcing | CaravanForcing`` -- and pydantic
    rejects anything that is not an instance of it, so the relationship has to
    be declared rather than merely implied. ``generate`` still resolves to
    :py:meth:`DestinEForcing.generate`; nothing from the ESMValTool recipe
    machinery is used.

    Examples:
        Lumped forcing for the Rhine over 2000, from the historical run:

        .. code-block:: python

            from pathlib import Path
            from ewatercycle.forcing import sources

            forcing = sources["DestinELumpedMakkinkForcing"].generate(
                start_time="2000-01-01T00:00:00Z",
                end_time="2000-12-31T00:00:00Z",
                directory="./destine_rhine_lumped",
                shape=Path("Rhine.shp"),
                variables=("pr", "tas", "evspsblpot"),
            )
            forcing["pr"]  # path to the precipitation file
    """

    lumped: ClassVar[bool] = True
