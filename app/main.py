from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from .config import (
    DEFAULT_AMBIENT_C, DEFAULT_WIND_MS
)
from .loaders import load_all, build_bus_lookup, build_conductor_lookup
from .rating import compute_line_ampacity, amps_to_mva
from .schemas import LineRating, Health

app = FastAPI(title="AEP Dynamic Line Ratings (IEEE-738)", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# Load once at startup
BUSES_DF, LINES_DF, CONDS_DF = load_all()
BUS = build_bus_lookup(BUSES_DF)
COND = build_conductor_lookup(CONDS_DF)

@app.get("/health", response_model=Health)
def health():
    return Health(status="ok", lines=len(LINES_DF), conductors=len(COND))

@app.get("/ratings", response_model=list[LineRating])
def ratings(
    ambient_c: float = Query(DEFAULT_AMBIENT_C, ge=-60, le=80),
    wind_ms: float   = Query(DEFAULT_WIND_MS, ge=0, le=60)
):
    out = []
    for _, r in LINES_DF.iterrows():
        conductor = str(r["conductor"])
        if conductor not in COND:
            raise HTTPException(400, f"Conductor '{conductor}' not found in conductor_library.csv")

        # Use bus0 voltage (these are 69/138 kV in your data; both ends match in this case)
        b0 = int(r["bus0"])
        if b0 not in BUS:
            raise HTTPException(400, f"Bus {b0} from line {r['name']} missing in buses.csv")

        kv = float(BUS[b0]["kv"])
        amps = compute_line_ampacity(r, kv, COND[conductor], ambient_c, wind_ms)
        mva  = amps_to_mva(amps, kv)

        out.append(LineRating(
            line_id=str(r["name"]),
            bus0=int(r["bus0"]), bus1=int(r["bus1"]),
            bus0_name=str(r.get("bus0_name") or BUS[b0]["busname"]),
            bus1_name=str(r.get("bus1_name") or BUS[int(r["bus1"])]["busname"]),
            conductor=conductor,
            mot_c=float(r.get("mot", 80.0)),
            voltage_kv=kv,
            amps=float(amps),
            mva=float(mva)
        ))
    return out

