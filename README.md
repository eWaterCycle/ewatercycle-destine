# eWaterCycle plugin: DestinE

Forcing for [eWaterCycle](https://github.com/eWaterCycle/ewatercycle) from the
[DestinE](https://destine.ecmwf.int/) Climate Digital Twin, read straight from
the zarr stores that the [Earth Data Hub](https://earthdatahub.destine.eu/catalogue)
serves.

## Prerequisites

A DestinE account with the Data Access Policy upgrade, and an Earth Data Hub
API key: log in at <https://platform.destine.eu/>, then *Menu → Quota & API Keys*.

Make the key available in one of two ways:

```console
export EDH_API_KEY=<your-api-key>
```

or in `~/.netrc` (`~/_netrc` on Windows), which survives across sessions:

```
machine api.earthdatahub.destine.eu
    login edh
    password <your-api-key>
```

## Installation

Install alongside your eWaterCycle installation:

```console
pip install ewatercycle-destine
```

Two forcing sources then become available:

```python
from ewatercycle.forcing import sources

sources["DestinEForcing"]        # gridded
sources["DestinELumpedForcing"]  # catchment-averaged
```

## Choosing a store

A store is addressed by three keys:

| key | values |
|---|---|
| `model` | `IFS-NEMO`, `IFS-FESOM`, `ICON` |
| `experiment` | `hist` (1990-2014), `cont`, `SSP3-7.0` (2015-2049) |
| `variant` | `standard`, `high-timeseries`, `high-maps` |

The variants trade resolution against coverage, and they are **not**
interchangeable:

| variant | resolution | variables | radiation |
|---|---|---|---|
| `standard` (default) | 0.35° | 37 | yes (`avg_sdswrf`) |
| `high-timeseries` | 0.044° | 7 | no |
| `high-maps` | 0.044° | 7, chunked for maps | no |

Makkink potential evaporation is derived from radiation, so `rsds` and
`evspsblpot` are only available from `standard`. Asking a high-resolution
variant for either raises a `ValueError` rather than quietly giving you
something else.

Variables are named as eWaterCycle expects them: `pr` (kg m-2 s-1), `tas` (K),
`rsds` (W m-2) and `evspsblpot` (kg m-2 s-1). Hourly store data is aggregated
to daily means.

## Lumped forcing

For a catchment-averaged time series, area-weighted by cos(latitude):

```python
from pathlib import Path
from ewatercycle.forcing import sources

forcing = sources["DestinELumpedForcing"].generate(
    start_time="2000-01-01T00:00:00Z",
    end_time="2000-12-31T00:00:00Z",
    directory="./forcing/rhine_lumped",
    shape=Path("Rhine.shp"),
    model="IFS-FESOM",
    experiment="hist",
)

forcing["pr"]        # path to the precipitation file
forcing.to_xarray()  # all variables in one dataset
```

## Distributed forcing

For the grid, clipped to the catchment outline:

```python
forcing = sources["DestinEForcing"].generate(
    start_time="2015-01-01T00:00:00Z",
    end_time="2015-12-31T00:00:00Z",
    directory="./forcing/rhine_gridded",
    shape=Path("Rhine.shp"),
    variables=("pr", "tas"),
    model="ICON",
    experiment="SSP3-7.0",
    variant="high-timeseries",  # 0.044 degree, no radiation
)
```

Only the variables you ask for are written. Derived ones pull in what they
need: `variables=("evspsblpot",)` fetches `tas` and `rsds` but writes only
`evspsblpot`.

## Reusing a forcing

`generate()` saves an `ewatercycle_forcing.yaml` next to the NetCDF files and
copies the shapefile in, all referenced by name. The directory can be moved or
shared, and read back with:

```python
forcing = sources["DestinELumpedForcing"].load("./forcing/rhine_lumped")
```

## Development

```console
pip install -e .[dev]
ruff check
mypy
pytest                 # no network
pytest -m integration  # hits the real store, needs an API key
```

`scripts/probe_store.py` prints what a store really contains (variables, dims,
coordinate order, chunking), which is the quickest way to check the values this
plugin hard-codes against the catalogue.

## License

`ewatercycle-destine` is distributed under the terms of the
[Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
