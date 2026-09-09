"""Addressing and opening the DestinE Climate DT stores on the Earth Data Hub.

The ``climate-dt-2`` collection publishes every Climate DT experiment as a zarr
store on a regular lat/lon grid. A store is addressed by three keys:

* ``model``: which climate model produced the run;
* ``experiment``: ``hist`` (1990-2014), ``cont``, or ``SSP3-7.0`` (2015-2049);
* ``variant``: the trade-off between resolution and variable coverage.

The variants are not interchangeable. ``standard`` is 0.35 degree but carries
radiation, so it is the only variant Makkink potential evaporation can be
derived from. ``high-timeseries`` and ``high-maps`` are 0.044 degree but carry
only seven variables, radiation not among them; asking them for ``rsds`` or
``evspsblpot`` raises a :py:class:`ValueError` rather than silently returning
something coarser than requested.

See https://earthdatahub.destine.eu/catalogue for the catalogue itself.
"""

import xarray as xr

from ewatercycle_destine.auth import storage_options

STORE_URL_TEMPLATE = (
    "https://api.earthdatahub.destine.eu/climate-dt-2/"
    "{model}-{experiment}-sfc-hourly-{variant}-v0.zarr"
)

MODELS = ("IFS-NEMO", "IFS-FESOM", "ICON")
EXPERIMENTS = ("hist", "cont", "SSP3-7.0")
VARIANTS = ("standard", "high-timeseries", "high-maps")

CMOR_NAMES = {"t2m": "tas", "avg_tprate": "pr", "avg_sdswrf": "rsds"}
"""Earth Data Hub short names mapped to the CMOR names eWaterCycle uses."""

STORE_NAMES = {cmor: store for store, cmor in CMOR_NAMES.items()}

ATTRIBUTES = {
    "tas": {
        "units": "K",
        "standard_name": "air_temperature",
        "long_name": "Air temperature at 2 m",
    },
    "pr": {
        "units": "kg m-2 s-1",
        "standard_name": "precipitation_flux",
        "long_name": "Precipitation",
    },
    "rsds": {
        "units": "W m-2",
        "standard_name": "surface_downwelling_shortwave_flux_in_air",
        "long_name": "Surface downwelling shortwave radiation",
    },
}
"""Attributes of the stored variables.

Both fluxes are stored as time-mean rates (``avg_tprate`` in kg m-2 s-1,
``avg_sdswrf`` in W m-2), which are already the CMOR units. Do not rescale
them: the /3.6 and /3600 conversions that the first-generation stores needed
(precipitation in m, radiation accumulated in J m-2) are wrong here.
"""

VARIANT_VARIABLES = {
    "standard": frozenset({"tas", "pr", "rsds"}),
    "high-timeseries": frozenset({"tas", "pr"}),
    "high-maps": frozenset({"tas", "pr"}),
}
"""Variables of interest to this plugin that each variant can supply."""

DERIVED_FROM = {"evspsblpot": ("tas", "rsds")}
"""Variables that are computed here rather than read from the store."""

DEFAULT_VARIABLES = ("pr", "tas", "rsds", "evspsblpot")

# The stores use latitude/longitude; CMOR, and so the rest of eWaterCycle,
# uses lat/lon. ewatercycle.util.merge_esvmaltool_datasets, which backs
# DefaultForcing.to_xarray(), insists on the CMOR names.
LAT, LON = "lat", "lon"
COORDINATE_NAMES = {"latitude": LAT, "longitude": LON}


def store_url(model: str, experiment: str, variant: str) -> str:
    """Return the Earth Data Hub URL of a Climate DT store.

    Args:
        model: One of :py:data:`MODELS`.
        experiment: One of :py:data:`EXPERIMENTS`.
        variant: One of :py:data:`VARIANTS`.

    Returns:
        The store URL, without credentials.

    Raises:
        ValueError: If any of the keys is not a known value.
    """
    for value, allowed, name in (
        (model, MODELS, "model"),
        (experiment, EXPERIMENTS, "experiment"),
        (variant, VARIANTS, "variant"),
    ):
        if value not in allowed:
            msg = f"Unknown {name} '{value}', expected one of {list(allowed)}."
            raise ValueError(msg)
    return STORE_URL_TEMPLATE.format(
        model=model, experiment=experiment, variant=variant
    )


def open_store(model: str, experiment: str, variant: str) -> xr.Dataset:
    """Lazily open a Climate DT zarr store on the Earth Data Hub.

    Args:
        model: One of :py:data:`MODELS`.
        experiment: One of :py:data:`EXPERIMENTS`.
        variant: One of :py:data:`VARIANTS`.

    Returns:
        The whole (global, hourly) store, opened lazily.
    """
    return xr.open_dataset(
        store_url(model, experiment, variant),
        engine="zarr",
        chunks="auto",
        storage_options=storage_options(),
    )


def resolve_variables(variables: tuple[str, ...], variant: str) -> set[str]:
    """Return the stored variables needed to produce the requested ones.

    Args:
        variables: CMOR names the caller asked for, derived ones included.
        variant: The variant the data will come from.

    Returns:
        The CMOR names that have to be read from the store.

    Raises:
        ValueError: If a variable is unknown to this plugin, or if the variant
            cannot supply it.
    """
    needed: set[str] = set()
    for variable in variables:
        needed.update(DERIVED_FROM.get(variable, (variable,)))

    unknown = needed - set(STORE_NAMES)
    if unknown:
        known = sorted(set(STORE_NAMES) | set(DERIVED_FROM))
        msg = f"Unknown variable(s) {sorted(unknown)}, expected some of {known}."
        raise ValueError(msg)

    missing = needed - VARIANT_VARIABLES[variant]
    if missing:
        msg = (
            f"Variant '{variant}' does not contain {sorted(missing)}, so "
            f"{sorted(set(variables) - VARIANT_VARIABLES[variant])} cannot be "
            f"produced from it. Use variant='standard' (0.35 degree), which is the "
            f"only variant carrying radiation."
        )
        raise ValueError(msg)
    return needed


def to_cmor_names(ds: xr.Dataset) -> xr.Dataset:
    """Rename a store's variables and coordinates to their CMOR names.

    Args:
        ds: Dataset as opened from the store.

    Returns:
        The dataset, with whichever of the known names it carried renamed.
    """
    renames = {**CMOR_NAMES, **COORDINATE_NAMES}
    return ds.rename({old: new for old, new in renames.items() if old in ds.variables})
