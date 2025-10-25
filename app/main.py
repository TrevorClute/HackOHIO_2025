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

        # compute ampacity safely (ieee738 may raise for invalid params)
        status = None
        try:
            amps = compute_line_ampacity(r, kv, COND[conductor], ambient_c, wind_ms)
            mva  = amps_to_mva(amps, kv)
        except Exception as e:
            # surface as a non-fatal status in the output for debugging
            amps = 0.0
            mva = 0.0
            status = str(e)

        # s_nom in the CSV appears to be MVA (s_nom column). Use if present.
        s_nom_mva = None
        try:
            s_nom_val = r.get("s_nom")
            if s_nom_val is not None and str(s_nom_val) != "":
                s_nom_mva = float(s_nom_val)
        except Exception:
            s_nom_mva = None

        # allow lines.csv to include per-line actuals (optional columns): actual_amps or actual_mva
        actual_amps = None
        actual_mva = None
        try:
            a_amps = r.get("actual_amps")
            a_mva = r.get("actual_mva")
            if a_amps is not None and str(a_amps) != "":
                actual_amps = float(a_amps)
            if a_mva is not None and str(a_mva) != "":
                actual_mva = float(a_mva)
        except Exception:
            actual_amps = None
            actual_mva = None

        # compute stress: prefer actual_amps, then actual_mva, then s_nom_mva
        stress_ratio = None
        stress_pct = None
        try:
            if actual_amps is not None and amps > 0:
                stress_ratio = float(actual_amps) / float(amps)
            elif actual_mva is not None and mva > 0:
                # convert actual_mva to ratio in MVA space
                stress_ratio = float(actual_mva) / float(mva) if mva > 0 else None
            elif s_nom_mva is not None and mva > 0:
                stress_ratio = float(s_nom_mva) / float(mva) if mva > 0 else None

            if stress_ratio is not None:
                stress_pct = float(stress_ratio) * 100.0
        except Exception:
            stress_ratio = None
            stress_pct = None

        # optional bus coordinates for frontend mapping
        bus0_lon = None
        bus0_lat = None
        bus1_lon = None
        bus1_lat = None
        try:
            b0_info = BUS.get(b0)
            if b0_info:
                bus0_lon = float(b0_info.get("lon")) if b0_info.get("lon") is not None else None
                bus0_lat = float(b0_info.get("lat")) if b0_info.get("lat") is not None else None
            b1 = int(r["bus1"])
            b1_info = BUS.get(b1)
            if b1_info:
                bus1_lon = float(b1_info.get("lon")) if b1_info.get("lon") is not None else None
                bus1_lat = float(b1_info.get("lat")) if b1_info.get("lat") is not None else None
        except Exception:
            pass

        out.append(LineRating(
            line_id=str(r["name"]),
            bus0=int(r["bus0"]), bus1=int(r["bus1"]),
            bus0_name=str(r.get("bus0_name") or BUS[b0]["busname"]),
            bus1_name=str(r.get("bus1_name") or BUS[int(r["bus1"])]["busname"]),
            bus0_lon=bus0_lon, bus0_lat=bus0_lat,
            bus1_lon=bus1_lon, bus1_lat=bus1_lat,
            conductor=conductor,
            mot_c=float(r.get("mot", 80.0)),
            voltage_kv=kv,
            amps=float(amps),
            mva=float(mva),
            s_nom_mva=s_nom_mva,
            actual_amps=actual_amps,
            actual_mva=actual_mva,
            stress_ratio=stress_ratio,
            stress_pct=stress_pct,
            status=status
        ))
    return out


@app.get("/ratings_geojson")
def ratings_geojson(
    ambient_c: float = Query(DEFAULT_AMBIENT_C, ge=-60, le=80),
    wind_ms: float   = Query(DEFAULT_WIND_MS, ge=0, le=60)
):
    """Return ratings as a GeoJSON FeatureCollection.

    Each feature is a LineString from bus0 -> bus1 with properties copied from the
    LineRating model (amps, mva, stress_pct, etc.). Missing coordinates result in
    a feature with null geometry but properties preserved.
    """
    # reuse the existing ratings function to compute values and preserve behavior
    ratings_list = ratings(ambient_c=ambient_c, wind_ms=wind_ms)

    def model_to_dict(m):
        # pydantic v2 uses model_dump(); v1 used dict(). Support both.
        if hasattr(m, "model_dump"):
            return m.model_dump()
        if hasattr(m, "dict"):
            return m.dict()
        return dict(m)

    features = []
    for r in ratings_list:
        rd = model_to_dict(r)
        lon0 = rd.get("bus0_lon")
        lat0 = rd.get("bus0_lat")
        lon1 = rd.get("bus1_lon")
        lat1 = rd.get("bus1_lat")

        if None not in (lon0, lat0, lon1, lat1):
            geometry = {
                "type": "LineString",
                "coordinates": [ [lon0, lat0], [lon1, lat1] ]
            }
        else:
            geometry = None

        # keep a compact set of properties for mapping clients
        props = {
            "line_id": rd.get("line_id"),
            "bus0": rd.get("bus0"),
            "bus1": rd.get("bus1"),
            "conductor": rd.get("conductor"),
            "mot_c": rd.get("mot_c"),
            "voltage_kv": rd.get("voltage_kv"),
            "amps": rd.get("amps"),
            "mva": rd.get("mva"),
            "s_nom_mva": rd.get("s_nom_mva"),
            "actual_amps": rd.get("actual_amps"),
            "actual_mva": rd.get("actual_mva"),
            "stress_ratio": rd.get("stress_ratio"),
            "stress_pct": rd.get("stress_pct"),
            "status": rd.get("status")
        }

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": props
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}

