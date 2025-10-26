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
from .stress import compute_stress_table, compute_ratings_table

import json
from fastapi.responses import JSONResponse
from .config import GIS_LINES_GEOJSON
from .stress import compute_ratings_table

# ---------- pydantic models ----------

class RatingOut(BaseModel):
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
    static_s_nom_mva: Optional[float] = None

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
    bad_threshold: float  = Query(BAD_THRESHOLD,  ge=0, le=100),
    elevation_ft: float = Query(0.0, ge=0, le=50000, description="Height above sea level in feet"),
    latitude_deg: float = Query(21.3, ge=-90, le=90, description="Latitude in degrees"),
    sun_time_hr: float = Query(12.0, ge=0, le=24, description="Hour of day (0-24)"),
    emissivity: float = Query(0.5, ge=0, le=1, description="Emissivity (0-1)"),
    absorptivity: float = Query(0.5, ge=0, le=1, description="Absorptivity (0-1)"),
    direction: str = Query("EastWest", description="Conductor orientation: EastWest or NorthSouth"),
    atmosphere: str = Query("Clear", description="Atmosphere type: Clear or Industrial"),
    date_str: str = Query("12 Jun", description="Date in format like '12 Jun'")
):
    df = compute_stress_table(
        BUSES, LINES, CONDS, FLOWS,
        ambient_c=ambient_c, wind_ms=wind_ms, wind_angle_deg=wind_angle_deg,
        warn_threshold=warn_threshold, bad_threshold=bad_threshold,
        elevation_ft=elevation_ft, latitude_deg=latitude_deg, sun_time_hr=sun_time_hr,
        emissivity=emissivity, absorptivity=absorptivity, direction=direction,
        atmosphere=atmosphere, date_str=date_str
    )
    if df.empty:
        raise HTTPException(
            400,
            "No output. Make sure: 1) flows.csv has 'name,p0_nominal' with non-empty MW per line, "
            "2) conductor names in lines.csv match conductor_library.csv exactly, "
            "3) buses.csv has v_nom (kV) for each line’s bus0."
        )
    return df.to_dict(orient="records")

@app.get("/ratings", response_model=List[RatingOut])
def ratings(
    ambient_c: float = Query(DEFAULT_AMBIENT_C, ge=-60, le=80),
    wind_ms: float   = Query(DEFAULT_WIND_MS, ge=0, le=60),
    wind_angle_deg: float = Query(DEFAULT_WIND_ANGLE_DEG, ge=0, le=90),
    include_static: bool = Query(True),
    elevation_ft: float = Query(0.0, ge=0, le=50000, description="Height above sea level in feet"),
    latitude_deg: float = Query(21.3, ge=-90, le=90, description="Latitude in degrees"),
    sun_time_hr: float = Query(12.0, ge=0, le=24, description="Hour of day (0-24)"),
    emissivity: float = Query(0.5, ge=0, le=1, description="Emissivity (0-1)"),
    absorptivity: float = Query(0.5, ge=0, le=1, description="Absorptivity (0-1)"),
    direction: str = Query("EastWest", description="Conductor orientation: EastWest or NorthSouth"),
    atmosphere: str = Query("Clear", description="Atmosphere type: Clear or Industrial"),
    date_str: str = Query("12 Jun", description="Date in format like '12 Jun'")
):
    df = compute_ratings_table(
        BUSES, LINES, CONDS,
        ambient_c=ambient_c,
        wind_ms=wind_ms,
        wind_angle_deg=wind_angle_deg,
        include_static=include_static,
        elevation_ft=elevation_ft, latitude_deg=latitude_deg, sun_time_hr=sun_time_hr,
        emissivity=emissivity, absorptivity=absorptivity, direction=direction,
        atmosphere=atmosphere, date_str=date_str
    )
    if df.empty:
        raise HTTPException(
            400,
            "No ratings computed. Check that lines.csv references conductors present in conductor_library.csv and buses.csv has v_nom."
        )
    return df.to_dict(orient="records")



def _pick_name(props: dict):
    # Join key: prefer "Name", fallback to "name"
    if not isinstance(props, dict):
        return None
    return str(props.get("Name") or props.get("name") or "").strip() or None

@app.get("/ratings_geojson")
def ratings_geojson(
    ambient_c: float = Query(DEFAULT_AMBIENT_C, ge=-60, le=80),
    wind_ms: float   = Query(DEFAULT_WIND_MS, ge=0, le=60),
    wind_angle_deg: float = Query(DEFAULT_WIND_ANGLE_DEG, ge=0, le=90),
    include_static: bool = Query(True, description="Include static s_nom from lines.csv"),
    include_unmatched: bool = Query(False, description="Keep features that did not match a line_id"),
    elevation_ft: float = Query(0.0, ge=0, le=50000, description="Height above sea level in feet"),
    latitude_deg: float = Query(21.3, ge=-90, le=90, description="Latitude in degrees"),
    sun_time_hr: float = Query(12.0, ge=0, le=24, description="Hour of day (0-24)"),
    emissivity: float = Query(0.5, ge=0, le=1, description="Emissivity (0-1)"),
    absorptivity: float = Query(0.5, ge=0, le=1, description="Absorptivity (0-1)"),
    direction: str = Query("EastWest", description="Conductor orientation: EastWest or NorthSouth"),
    atmosphere: str = Query("Clear", description="Atmosphere type: Clear or Industrial"),
    date_str: str = Query("12 Jun", description="Date in format like '12 Jun'")
):
    # 1) compute dynamic ratings table
    df = compute_ratings_table(
        BUSES, LINES, CONDS,
        ambient_c=ambient_c,
        wind_ms=wind_ms,
        wind_angle_deg=wind_angle_deg,
        include_static=include_static,
        elevation_ft=elevation_ft, latitude_deg=latitude_deg, sun_time_hr=sun_time_hr,
        emissivity=emissivity, absorptivity=absorptivity, direction=direction,
        atmosphere=atmosphere, date_str=date_str
    )
    if df.empty:
        raise HTTPException(400, "No ratings computed. Check conductors/buses/lines inputs.")

    # 2) index by line_id for fast join
    lut = df.set_index("line_id").to_dict(orient="index")

    # 3) load GeoJSON features from disk
    if not GIS_LINES_GEOJSON.exists():
        raise HTTPException(404, f"GeoJSON not found: {GIS_LINES_GEOJSON}")
    with GIS_LINES_GEOJSON.open("r", encoding="utf-8") as f:
        gj = json.load(f)

    features = gj.get("features", [])
    out_features = []

    for feat in features:
        props = feat.get("properties", {}) or {}
        line_id = _pick_name(props)
        row = lut.get(line_id)

        if row is None and not include_unmatched:
            # skip features we can't enrich (no matching line_id)
            continue

        # Merge properties; keep original geometry unchanged
        new_props = dict(props)
        new_props.update({
            # Include the id we matched on for debugging
            "line_id": line_id,
            # Dynamic ratings payload
            "voltage_kv": row.get("voltage_kv") if row else None,
            "conductor": row.get("conductor") if row else None,
            "mot_c": row.get("mot_c") if row else None,
            "rating_amps": row.get("rating_amps") if row else None,
            "rating_mva": row.get("rating_mva") if row else None,
            # Optional static rating
            "static_s_nom_mva": row.get("static_s_nom_mva") if row else None,
            # Weather echo for client transparency
            "_ambient_c": ambient_c,
            "_wind_ms": wind_ms,
            "_wind_angle_deg": wind_angle_deg,
            "_dynamic": True,
        })

        out_features.append({
            "type": "Feature",
            "geometry": feat.get("geometry"),
            "properties": new_props,
        })

    fc = {"type": "FeatureCollection", "features": out_features}
    return JSONResponse(fc)

