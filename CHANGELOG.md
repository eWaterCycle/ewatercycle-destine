# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-16

First release. The 0.0.x prototype was never published, so everything below is
new to anyone installing from PyPI.

### Added

- `DestinEForcing`, a `DistributedMakkinkForcing` that writes the DestinE grid
  clipped to a catchment outline.
- `DestinELumpedMakkinkForcing`, a `LumpedMakkinkForcing` that writes a
  catchment-averaged time series, area-weighted by cos(latitude). Both are
  registered as eWaterCycle forcing sources, so models that annotate their
  forcing field with those types — HBV among them — accept them directly.
- Store selection by `model` (`IFS-NEMO`, `IFS-FESOM`, `ICON`), `experiment`
  (`hist`, `cont`, `SSP3-7.0`) and `variant` (`standard`, `high-timeseries`,
  `high-maps`). Asking a high-resolution variant for `rsds` or `evspsblpot`
  raises a `ValueError` instead of quietly returning something else, because
  those variants carry no radiation.
- Variables named as eWaterCycle expects them — `pr`, `tas`, `rsds` and
  `evspsblpot` — with hourly store data aggregated to daily means, and Makkink
  potential evaporation derived from radiation. Only requested variables are
  written; derived ones fetch what they need.
- `generate()` writes an `ewatercycle_forcing.yaml` beside the NetCDF files and
  copies the shapefile in, all referenced by name, so a forcing directory can be
  moved or shared and read back with `load()`.
- Earth Data Hub authentication from `EDH_API_KEY` or `~/.netrc`
  (`~/_netrc` on Windows).
- `scripts/setup_env.py`, which creates or repairs a `.env` file and can check
  the key against the Hub, and `scripts/probe_store.py`, which prints what a
  store actually contains (variables, dims, coordinate order, chunking).
- Two worked notebooks in `docs/`: `destine_forcing.ipynb` (the plugin end to
  end, lumped and distributed, historical and scenario) and
  `forcings_with_hbv.ipynb` (HBV run on Caravan, ERA5, ERA5-Land and DestinE
  forcing side by side).
- A test suite that does not touch the network, plus integration tests behind
  the `integration` marker, deselected by default.
- Ruff and mypy configuration, and a CI workflow that runs them with the tests.

### Changed

- Forcing generation now reads the Earth Data Hub `climate-dt-2` zarr stores
  directly, replacing the earlier bespoke download path.
- Authentication moved from DESP Keycloak to an Earth Data Hub API key.
- Requires Python 3.12 or newer and `ewatercycle>=2.6.0`; zarr 3 is required
  because the Earth Data Hub stores are zarr v3.

### Removed

- The DESP Keycloak authentication modules (`desp-authentication.py`,
  `dest_auth.py`).
- The unused ECMWF parameter table.

[Unreleased]: https://github.com/eWaterCycle/ewatercycle-destine/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eWaterCycle/ewatercycle-destine/releases/tag/v0.1.0
