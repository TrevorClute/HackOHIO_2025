from pydantic import BaseModel
from typing import Optional

class LineRating(BaseModel):
    line_id: str
    bus0: int
    bus1: int
    bus0_name: Optional[str] = None
    bus1_name: Optional[str] = None
    conductor: str
    mot_c: float
    voltage_kv: float
    amps: float
    mva: float

class Health(BaseModel):
    status: str
    lines: int
    conductors: int

