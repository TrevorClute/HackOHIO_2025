## Quick orientation — what this repo is

This project is a small FastAPI service that computes IEEE-738 conductor ampacity and returns per-line ratings (amps and MVA) based on CSV data uploaded into the `data/` folder. The service entrypoint is `app/main.py` and it exposes two endpoints: `/health` and `/ratings`.

## Key files to read first
- `app/main.py` — FastAPI app, startup data load (calls `load_all()`), and the `/ratings` logic.
- `app/loaders.py` — CSV loading and lookups. Normalizes column names to lower-case and builds `BUS` and `COND` dicts used by the API.
- `app/rating.py` — glue between CSV rows and `ieee738` conductor calculations (conversions, parameter mapping, amps → MVA).
- `ieee738.py` — implementation of IEEE-738 conductor math (ConductorParams + Conductor). Imported from repo root by `app/rating.py` using a sys.path insert.
- `app/config.py` — default env vars and unit conversion constants (e.g. OHM_PER_MILE_TO_OHM_PER_FT, MS_TO_FPS).
- `app/schemas.py` — pydantic response models used by endpoints.

## Big-picture architecture and flows (short)
- Startup: `app/main.py` imports `load_all()` and builds global `BUSES_DF`, `LINES_DF`, `CONDS_DF` and two lookup dicts (`BUS`, `COND`). Data is loaded once at import time and reused on each request.
- Request flow: `/ratings` iterates `LINES_DF` rows, finds conductor and bus via the lookups, converts units, calls `compute_line_ampacity()` in `app/rating.py`, then maps result into `LineRating` pydantic models.
- Important conversion responsibilities live in `app/rating.py`: wind m/s → ft/s, ohm/mile → ohm/ft, and MOT temperature handling.

## Project-specific conventions and gotchas
- CSV column normalization: `load_all()` lower-cases headers. But `build_bus_lookup()` renames `name→bus_id`, `v_nom→kv`, `x→lon`, `y→lat`. When changing CSV format update both `loaders.py` and the rename logic.
- Required CSV columns (discoverable from `loaders.py` comments):
  - buses.csv: `name` (int bus id), `v_nom` (kV), `x` (lon), `y` (lat), `BusName`
  - lines.csv: `name`, `bus0`, `bus1`, `conductor`, `mot`, `s_nom`, `bus0_name`, `bus1_name`, `conductorsperbundle`
  - conductor_library.csv: `conductorname`, `res_25c`, `res_50c`, `cdrad_in`, `cdgmr_ft`
- The code expects conductor names (string) to match keys in the conductor CSV. Missing conductor or bus causes an HTTP 400 (see `app/main.py`).
- The repo-level `ieee738.py` uses ohm/ft; loaders convert ohm/mile to ohm/ft before instantiating `ConductorParams`.
- `app/rating.py` inserts the repo root into `sys.path` to import `ieee738`. If refactoring/packaging, either make `ieee738` a proper package or adjust imports.

## How to run locally (what works in this repo)
1. Create a venv and install requirements (this is replicated in `README.md`):

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Start the dev server:

   uvicorn app.main:app --reload --port 8000

3. Example query (returns JSON list of LineRating):

   GET http://localhost:8000/ratings?ambient_c=30&wind_ms=2

or quick curl:

   curl 'http://localhost:8000/ratings?ambient_c=30&wind_ms=2'

Notes: wind_ms is meters/sec (converted internally to ft/s). Defaults are in `app/config.py`.

## What to change carefully
- If you change CSV column names or add new fields, update `loaders.py` normalize/rename steps and `build_*_lookup` functions.
- If you change units (e.g., switch to ft/s input), update conversions in `app/rating.py` and document the new API contract.
- Avoid moving `ieee738.py` without adjusting the import in `app/rating.py` (or turning it into a package import).

## Quick examples for codegen tasks
- Add a new optional query parameter to `/ratings`: modify `app/main.py` handler signature and add handling in the loop. Use `Query(...)` like existing `ambient_c`/`wind_ms` examples.
- Add a new derived field to response: update `app/schemas.py` with a new pydantic field and populate it when constructing the `LineRating` objects in `app/main.py`.

## Local testing notes
- There are no unit tests in the repo. For quick checks, run the server and call `/health` and `/ratings`.
- Watch for exceptions raised by `ieee738` (value errors when solar or radiative terms compute zero) — they can surface as 500s during incorrect parameter choices.

If any of these points are unclear or you want me to expand a section (examples for adding a parameter, turning `ieee738` into an importable package, or adding unit tests), tell me which area to iterate on.
