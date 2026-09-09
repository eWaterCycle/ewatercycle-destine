"""Tests for store addressing and the variable/variant bookkeeping."""

import pytest

from ewatercycle_destine.store import (
    ATTRIBUTES,
    CMOR_NAMES,
    resolve_variables,
    store_url,
)


def test_store_url():
    assert store_url("IFS-NEMO", "SSP3-7.0", "high-maps") == (
        "https://api.earthdatahub.destine.eu/climate-dt-2/"
        "IFS-NEMO-SSP3-7.0-sfc-hourly-high-maps-v0.zarr"
    )


@pytest.mark.parametrize(
    ("model", "experiment", "variant"),
    [
        ("IFS-TYPO", "hist", "standard"),
        ("ICON", "historical", "standard"),
        ("ICON", "hist", "high"),
    ],
)
def test_store_url_rejects_unknown_keys(model, experiment, variant):
    with pytest.raises(ValueError, match="expected one of"):
        store_url(model, experiment, variant)


def test_names_map_to_cmor():
    assert CMOR_NAMES == {"t2m": "tas", "avg_tprate": "pr", "avg_sdswrf": "rsds"}


def test_units_are_the_stored_ones():
    # The store holds time-mean rates in exactly these units, so nothing needs
    # converting. See test_forcing.py for the test that nothing is converted.
    assert ATTRIBUTES["pr"]["units"] == "kg m-2 s-1"
    assert ATTRIBUTES["rsds"]["units"] == "W m-2"
    assert ATTRIBUTES["tas"]["units"] == "K"


def test_resolve_variables_passes_stored_variables_through():
    assert resolve_variables(("pr", "tas"), "standard") == {"pr", "tas"}


def test_resolve_variables_expands_derived_variables():
    assert resolve_variables(("pr", "evspsblpot"), "standard") == {"pr", "tas", "rsds"}


def test_resolve_variables_rejects_unknown_variables():
    with pytest.raises(ValueError, match="Unknown variable"):
        resolve_variables(("pr", "windspeed"), "standard")


@pytest.mark.parametrize("variant", ["high-timeseries", "high-maps"])
@pytest.mark.parametrize("variable", ["rsds", "evspsblpot"])
def test_high_resolution_variants_have_no_radiation(variant, variable):
    with pytest.raises(ValueError, match="variant='standard'") as excinfo:
        resolve_variables(("pr", "tas", variable), variant)
    assert variable in str(excinfo.value)


@pytest.mark.parametrize("variant", ["high-timeseries", "high-maps"])
def test_high_resolution_variants_still_serve_pr_and_tas(variant):
    assert resolve_variables(("pr", "tas"), variant) == {"pr", "tas"}
