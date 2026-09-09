"""Report what the Earth Data Hub stores actually contain.

The slugs, variable names and coordinate order this plugin assumes were read
off the public catalogue pages, which need an API key to verify. Run this with
a key to check them against the real thing::

    python scripts/probe_store.py                 # every combination
    python scripts/probe_store.py IFS-FESOM hist  # one model/experiment

For each store it prints whether it opens, its variables, dimensions, the
latitude order, the longitude convention and the chunking, which is everything
ewatercycle_destine.processing relies on.
"""

import sys
import traceback

from ewatercycle_destine.store import (
    CMOR_NAMES,
    EXPERIMENTS,
    MODELS,
    VARIANTS,
    open_store,
    store_url,
)


def describe(model: str, experiment: str, variant: str) -> None:
    """Print what one store contains, or why it could not be opened."""
    print(f"\n=== {model} / {experiment} / {variant}")
    print(f"    {store_url(model, experiment, variant)}")
    try:
        ds = open_store(model, experiment, variant)
    except Exception:  # noqa: BLE001 - a probe reports failures, it does not raise
        print("    FAILED to open:")
        for line in traceback.format_exc(limit=1).strip().splitlines():
            print(f"      {line}")
        return

    print(f"    dims:       {dict(ds.sizes)}")
    print(f"    variables:  {sorted(ds.data_vars)}")
    missing = [name for name in CMOR_NAMES if name not in ds.data_vars]
    print(f"    expected but absent: {missing or 'none'}")

    for name in sorted(set(CMOR_NAMES) & set(ds.data_vars)):
        variable = ds[name]
        print(
            f"      {name}: units={variable.attrs.get('units')!r} "
            f"chunks={variable.chunks and [c[0] for c in variable.chunks]}"
        )

    for name in ("latitude", "lat"):
        if name in ds.coords:
            values = ds[name].to_numpy()
            order = "descending" if values[0] > values[-1] else "ascending"
            print(
                f"    {name}: {values[0]} .. {values[-1]} "
                f"({order}, n={values.size})"
            )
    for name in ("longitude", "lon"):
        if name in ds.coords:
            values = ds[name].to_numpy()
            print(f"    {name}: {values.min()} .. {values.max()} (n={values.size})")
    if "time" in ds.coords:
        time = ds["time"]
        print(
            f"    time: {time[0].to_numpy()} .. {time[-1].to_numpy()} "
            f"(n={time.size})"
        )


def main(argv: list[str]) -> None:
    """Probe every store, or the ones named on the command line."""
    models = [argv[0]] if len(argv) > 0 else list(MODELS)
    experiments = [argv[1]] if len(argv) > 1 else list(EXPERIMENTS)
    variants = [argv[2]] if len(argv) > 2 else list(VARIANTS)

    for model in models:
        for experiment in experiments:
            for variant in variants:
                describe(model, experiment, variant)


if __name__ == "__main__":
    main(sys.argv[1:])
