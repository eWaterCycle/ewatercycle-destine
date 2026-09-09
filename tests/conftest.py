"""Fixtures backing the tests: a synthetic store and the Rhine test catchment.

The default test run never touches the network. `synthetic_store` mimics the
Earth Data Hub layout closely enough for the processing chain: the store's own
short names, hourly time steps, a regular lat/lon grid with *descending*
latitudes and longitudes on -180..180.
"""

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from ewatercycle.testing.fixtures import rhine_shape

# Constant values, so any rescaling shows up as an exact mismatch.
TAS_VALUE = 283.15  # K
TPRATE_VALUE = 1e-5  # kg m-2 s-1, a time-mean rate, not an accumulation
SDSWRF_VALUE = 200.0  # W m-2, a time-mean rate, not an accumulation


def make_store(
    start: str = "2000-01-01",
    days: int = 3,
    resolution: float = 0.5,
    descending_latitude: bool = True,
) -> xr.Dataset:
    """Build a synthetic Earth Data Hub store covering the Rhine."""
    time = pd.date_range(start, periods=24 * days, freq="h")
    latitudes = np.arange(45.0, 53.0 + resolution / 2, resolution)
    if descending_latitude:
        latitudes = latitudes[::-1]
    longitudes = np.arange(3.0, 13.0 + resolution / 2, resolution)

    shape = (time.size, latitudes.size, longitudes.size)
    dims = ("time", "latitude", "longitude")
    coords = {"time": time, "latitude": latitudes, "longitude": longitudes}

    return xr.Dataset(
        {
            "t2m": (dims, np.full(shape, TAS_VALUE)),
            "avg_tprate": (dims, np.full(shape, TPRATE_VALUE)),
            "avg_sdswrf": (dims, np.full(shape, SDSWRF_VALUE)),
        },
        coords=coords,
    )


@pytest.fixture
def synthetic_store() -> xr.Dataset:
    """A synthetic store covering the Rhine, for three hourly days."""
    return make_store()


@pytest.fixture
def rhine() -> str:
    """Path to the Rhine shapefile shipped with ewatercycle."""
    return str(rhine_shape())
