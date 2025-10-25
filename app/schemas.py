from pydantic import BaseModel
from typing import Optional


class LineRating(BaseModel):
    # identity
    line_id: str
    bus0: int
    bus1: int
    bus0_name: Optional[str] = None
    bus1_name: Optional[str] = None
    # optional coordinates for frontend mapping (added from BUS lookup)
    bus0_lon: Optional[float] = None
    bus0_lat: Optional[float] = None
    bus1_lon: Optional[float] = None
    bus1_lat: Optional[float] = None

    conductor: str
    mot_c: float
    voltage_kv: float

    # computed ratings
    amps: float
    mva: float

    # original/actual fields (if present in lines.csv)
    s_nom_mva: Optional[float] = None
    actual_amps: Optional[float] = None
    actual_mva: Optional[float] = None

    # derived stress metrics (actual or s_nom compared to computed)
    stress_ratio: Optional[float] = None
    stress_pct: Optional[float] = None

    # optional status / error message
    status: Optional[str] = None


class Health(BaseModel):
    status: str
    lines: int
    conductors: int

