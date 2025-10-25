from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

from .config import (
    DEFAULT_AMBIENT_C, DEFAULT_WIND_MS, DEFAULT_WIND_ANGLE_DEG,
    WARN_THRESHOLD, BAD_THRESHOLD
)
from .io import load_buses, load_lines, load_conductors, load_flows
from .stress import compute_stress_table

# ---------- pydantic models ----------
class StressOut(BaseModel):
    line_id: str
    bus0: int
    bus1: int
    bus0_name: Optional[str] = None
    bus1_name: Optional[str] = None
    conductor: str
    voltage_kv: float
    mot_c: float
    rating_amps: float
    rating_mva: float
    flow_amps: float
    flow_mva: float
    utilization_pct: float
    status: str
    overloaded: bool
    ampacity_margin_a: float
    mva_margin: float

class HealthOut(BaseModel):
    status: str
    lines: int
    flows: int
    conductors: int
    buses: int
    uses_ieee738: bool

# ---------- app ----------
app = FastAPI(title="Grid Criticality API (IEEE-738)", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# load at startup
BUSES = load_buses()
LINES = load_lines()
CONDS = load_conductors()
FLOWS = load_flows()

@app.get("/health", response_model=HealthOut)
def health():
    # a quick import probe (if import fails, app wouldn't have started)
    uses_ieee = True
    return HealthOut(
        status="ok",
        lines=len(LINES),
        flows=len(FLOWS),
        conductors=len(CONDS),
        buses=len(BUSES),
        uses_ieee738=uses_ieee
    )

@app.get("/stress_summary", response_model=List[StressOut])
def stress_summary(
    ambient_c: float = Query(DEFAULT_AMBIENT_C, ge=-60, le=80),
    wind_ms: float   = Query(DEFAULT_WIND_MS, ge=0, le=60),
    wind_angle_deg: float = Query(DEFAULT_WIND_ANGLE_DEG, ge=0, le=90),
    warn_threshold: float = Query(WARN_THRESHOLD, ge=0, le=100),
    bad_threshold: float  = Query(BAD_THRESHOLD,  ge=0, le=100)
):
    df = compute_stress_table(
        BUSES, LINES, CONDS, FLOWS,
        ambient_c=ambient_c, wind_ms=wind_ms, wind_angle_deg=wind_angle_deg,
        warn_threshold=warn_threshold, bad_threshold=bad_threshold
    )
    if df.empty:
        raise HTTPException(
            400,
            "No output. Make sure: 1) flows.csv has 'name,p0_nominal' with non-empty MW per line, "
            "2) conductor names in lines.csv match conductor_library.csv exactly, "
            "3) buses.csv has v_nom (kV) for each line’s bus0."
        )
    return df.to_dict(orient="records")

