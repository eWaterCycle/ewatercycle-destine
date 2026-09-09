"""Tests that hit the real Earth Data Hub.

Deselected by default (see ``addopts`` in pyproject.toml). Run them with an
API key in ``EDH_API_KEY`` or ``~/.netrc``::

    pytest -m integration
"""

import pytest

from ewatercycle_destine.auth import MissingApiKeyError, get_credentials
from ewatercycle_destine.forcing import DestinELumpedForcing
from ewatercycle_destine.store import open_store

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _needs_api_key():
    try:
        get_credentials()
    except MissingApiKeyError as error:
        pytest.skip(str(error))


def test_generate_from_the_real_store(tmp_path, rhine):
    forcing = DestinELumpedForcing.generate(
        start_time="2000-06-01T00:00:00Z",
        end_time="2000-06-03T23:00:00Z",
        directory=tmp_path,
        shape=rhine,
        model="IFS-FESOM",
        experiment="hist",
        variant="standard",
    )

    assert set(forcing.filenames) == {"pr", "tas", "rsds", "evspsblpot"}

    ds = forcing.to_xarray()
    assert ds.sizes["time"] == 3
    # Plausible daily values for the Rhine in June, in CMOR units. Mostly a
    # check that no stray unit conversion crept back in.
    assert 270 < float(ds["tas"].mean()) < 310
    assert 0 <= float(ds["pr"].mean()) < 1e-3
    assert 50 < float(ds["rsds"].mean()) < 500

    assert DestinELumpedForcing.load(tmp_path) == forcing


def test_store_layout_matches_what_the_code_assumes():
    """The store details the processing chain relies on."""
    ds = open_store("IFS-FESOM", "hist", "standard")

    assert {"t2m", "avg_tprate", "avg_sdswrf"} <= set(ds.data_vars)
    assert {"time", "latitude", "longitude"} <= set(ds.dims)
    assert float(ds["longitude"].max()) <= 180.0
