"""Tests for the forcing classes, with the store monkeypatched away."""

import shutil

import pytest
import xarray as xr
from conftest import SDSWRF_VALUE, TAS_VALUE, TPRATE_VALUE
from ewatercycle.forcing import CaravanForcing, LumpedMakkinkForcing
from pydantic import BaseModel

import ewatercycle_destine.forcing as forcing_module
from ewatercycle_destine.forcing import DestinEForcing, DestinELumpedMakkinkForcing

START = "2000-01-01T00:00:00Z"
END = "2000-01-03T23:00:00Z"


@pytest.fixture
def opened_stores(monkeypatch, synthetic_store):
    """Replace the store with a synthetic one, recording how it was asked for."""
    calls = []

    def fake_open_store(model, experiment, variant):
        calls.append((model, experiment, variant))
        return synthetic_store.copy(deep=True)

    monkeypatch.setattr(forcing_module, "open_store", fake_open_store)
    return calls


@pytest.fixture
def lumped_forcing(tmp_path, rhine, opened_stores):
    return DestinELumpedMakkinkForcing.generate(
        start_time=START, end_time=END, directory=tmp_path, shape=rhine
    )


def test_generate_writes_every_requested_variable(lumped_forcing, tmp_path):
    assert set(lumped_forcing.filenames) == {"pr", "tas", "rsds", "evspsblpot"}
    for filename in lumped_forcing.filenames.values():
        assert (tmp_path / filename).is_file()


def test_generate_uses_the_documented_defaults(lumped_forcing, opened_stores):
    assert opened_stores == [("IFS-FESOM", "hist", "standard")]


def test_fluxes_are_not_rescaled(lumped_forcing):
    """The store holds time-mean rates; /3.6 and /3600 would be wrong here."""
    precipitation = xr.open_dataarray(lumped_forcing["pr"])
    radiation = xr.open_dataarray(lumped_forcing["rsds"])

    assert float(precipitation.mean()) == pytest.approx(TPRATE_VALUE)
    assert float(radiation.mean()) == pytest.approx(SDSWRF_VALUE)
    # The conversions the first-generation stores needed, spelled out so a
    # reintroduced one fails here rather than silently in the water balance.
    assert float(precipitation.mean()) != pytest.approx(TPRATE_VALUE / 3.6)
    assert float(radiation.mean()) != pytest.approx(SDSWRF_VALUE / 3600)


def test_temperature_stays_in_kelvin(lumped_forcing):
    temperature = xr.open_dataarray(lumped_forcing["tas"])
    assert float(temperature.mean()) == pytest.approx(TAS_VALUE)
    assert temperature.attrs["units"] == "K"


def test_units_are_cmor_units(lumped_forcing):
    units = {
        variable: xr.open_dataarray(lumped_forcing[variable]).attrs["units"]
        for variable in lumped_forcing.filenames
    }
    assert units == {
        "pr": "kg m-2 s-1",
        "tas": "K",
        "rsds": "W m-2",
        "evspsblpot": "kg m-2 s-1",
    }


def test_hourly_data_is_aggregated_to_daily(lumped_forcing):
    assert xr.open_dataarray(lumped_forcing["pr"]).sizes["time"] == 3


def test_variables_are_honoured(tmp_path, rhine, opened_stores):
    forcing = DestinELumpedMakkinkForcing.generate(
        start_time=START,
        end_time=END,
        directory=tmp_path,
        shape=rhine,
        variables=("pr",),
    )

    assert set(forcing.filenames) == {"pr"}
    written = {path.name for path in tmp_path.glob("*.nc")}
    assert written == {forcing.filenames["pr"]}


def test_derived_variables_pull_in_what_they_need(tmp_path, rhine, opened_stores):
    """evspsblpot needs tas and rsds, but only evspsblpot was asked for."""
    forcing = DestinELumpedMakkinkForcing.generate(
        start_time=START,
        end_time=END,
        directory=tmp_path,
        shape=rhine,
        variables=("evspsblpot",),
    )

    assert set(forcing.filenames) == {"evspsblpot"}
    assert {path.name for path in tmp_path.glob("*.nc")} == {
        forcing.filenames["evspsblpot"]
    }
    evaporation = xr.open_dataarray(forcing["evspsblpot"])
    assert float(evaporation.mean()) > 0


@pytest.mark.parametrize("variable", ["rsds", "evspsblpot"])
def test_variant_without_radiation_is_refused(
    tmp_path, rhine, opened_stores, variable
):
    with pytest.raises(ValueError, match="variant='standard'"):
        DestinELumpedMakkinkForcing.generate(
            start_time=START,
            end_time=END,
            directory=tmp_path,
            shape=rhine,
            variables=("pr", "tas", variable),
            variant="high-timeseries",
        )
    # Refused before any data was fetched, rather than silently downgraded.
    assert opened_stores == []


def test_lumped_forcing_has_no_grid(lumped_forcing):
    precipitation = xr.open_dataarray(lumped_forcing["pr"])
    assert set(precipitation.dims) == {"time"}
    # The catchment centroid is kept as a scalar coordinate, so the file still
    # says where it is.
    assert 46 < float(precipitation["lat"]) < 53
    assert 4 < float(precipitation["lon"]) < 12


def test_forcing_can_be_opened_as_one_dataset(lumped_forcing):
    ds = lumped_forcing.to_xarray()
    assert set(ds.data_vars) == {"pr", "tas", "rsds", "evspsblpot"}
    assert ds.sizes["time"] == 3


def test_distributed_forcing_keeps_the_grid(tmp_path, rhine, opened_stores):
    forcing = DestinEForcing.generate(
        start_time=START,
        end_time=END,
        directory=tmp_path,
        shape=rhine,
        variables=("pr",),
    )
    precipitation = xr.open_dataarray(forcing["pr"])
    assert set(precipitation.dims) == {"time", "lat", "lon"}
    assert precipitation.sizes["lat"] > 1


def test_filenames_are_basenames(lumped_forcing):
    for filename in lumped_forcing.filenames.values():
        assert "/" not in filename
        assert "\\" not in filename


def test_saved_yaml_holds_no_absolute_paths(lumped_forcing, tmp_path):
    contents = (tmp_path / "ewatercycle_forcing.yaml").read_text()
    assert str(tmp_path) not in contents
    assert tmp_path.name not in contents


def test_round_trip(lumped_forcing, tmp_path):
    reloaded = DestinELumpedMakkinkForcing.load(tmp_path)
    assert reloaded == lumped_forcing


def test_forcing_directory_can_be_moved(lumped_forcing, tmp_path):
    elsewhere = tmp_path.parent / "moved"
    shutil.copytree(tmp_path, elsewhere)

    reloaded = DestinELumpedMakkinkForcing.load(elsewhere)

    assert reloaded.directory == elsewhere
    assert reloaded["pr"].is_file()
    assert reloaded.filenames == lumped_forcing.filenames
    assert reloaded.to_xarray()["pr"].sizes["time"] == 3


def test_shape_is_copied_next_to_the_data(lumped_forcing, tmp_path):
    assert lumped_forcing.shape == tmp_path / "Rhine.shp"
    assert lumped_forcing.get_shape_area() > 0


def test_lumped_forcing_is_a_makkink_forcing():
    assert issubclass(DestinELumpedMakkinkForcing, LumpedMakkinkForcing)


def test_lumped_forcing_is_accepted_where_models_expect_makkink(lumped_forcing):
    """HBV, and models like it, annotate the field with a union of types.

    Pydantic rejects anything that is not an instance of one of them, so a
    forcing that merely looks like a lumped Makkink forcing is not enough.
    """

    class ModelLikeHBV(BaseModel):
        forcing: LumpedMakkinkForcing | CaravanForcing

    model = ModelLikeHBV(forcing=lumped_forcing)

    assert model.forcing.filenames == lumped_forcing.filenames
