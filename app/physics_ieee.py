import sys
from pathlib import Path
import numpy as np
from math import sqrt
from .config import MS_TO_FPS, MILES_TO_FEET, ELEVATION_FT, LATITUDE_DEG, SUNTIME_HR, EMISSIVITY, ABSORPTIVITY, DIRECTION, ATMOSPHERE, DATE_STR

# ensure repo root is importable so we can import ieee738.py at project root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# must import user's ieee738
import ieee738
from ieee738 import Conductor, ConductorParams

# ----- conversions -----
def amps_to_mva(i_a: float, kv: float) -> float:
    return float(np.sqrt(3.0) * i_a * kv * 1e-3)

def mva_to_amps(s_mva: float, kv: float) -> float:
    return float((s_mva * 1e6) / (np.sqrt(3.0) * kv * 1e3))

def mw_to_amps(p_mw: float, kv: float, pf: float = 1.0) -> float:
    s_mva = float(p_mw) / float(pf if pf else 1.0)
    return mva_to_amps(s_mva, kv)

# ----- IEEE-738 adapter -----
def ieee738_rating_amps_from_rows(conductor_row: dict,
                                  mot_c: float,
                                  ambient_c: float,
                                  wind_ms: float,
                                  wind_angle_deg: float,
                                  elevation_ft: float = 0.0,
                                  latitude_deg: float = 21.3,
                                  sun_time_hr: float = 12.0,
                                  emissivity: float = 0.5,
                                  absorptivity: float = 0.5,
                                  direction: str = "EastWest",
                                  atmosphere: str = "Clear",
                                  date_str: str = "12 Jun") -> float:
    """
    Build ConductorParams from CSV fields and call Conductor(...).steady_state_thermal_rating()
    conductor_row requires:
      - res_25c_ohm_per_mile
      - res_50c_ohm_per_mile
      - diameter_in
      - conductors_per_bundle (default 1)
    """
    # required fields check
    for k in ("res_25c_ohm_per_mile", "res_50c_ohm_per_mile", "diameter_in"):
        if k not in conductor_row or conductor_row[k] is None:
            raise ValueError(f"Conductor library missing required field: {k}")

    # convert to ieee units (ohm/ft, inches, ft/s)
    r25_ft = float(conductor_row["res_25c_ohm_per_mile"]) / MILES_TO_FEET
    r50_ft = float(conductor_row["res_50c_ohm_per_mile"]) / MILES_TO_FEET
    diameter_in = float(conductor_row["diameter_in"])
    bundle = int(conductor_row.get("conductors_per_bundle", 1))
    wind_fps = float(wind_ms) * MS_TO_FPS

    params = ConductorParams(
        # ambient/environment
        Ta=ambient_c,
        WindVelocity=wind_fps,
        WindAngleDeg=float(max(0.0, min(90.0, wind_angle_deg))),
        Elevation=elevation_ft,
        Latitude=latitude_deg,
        SunTime=sun_time_hr,
        Emissivity=emissivity,
        Absorptivity=absorptivity,
        Direction=direction,       # 'EastWest' or 'NorthSouth'
        Atmosphere=atmosphere,     # 'Clear' or 'Industrial'
        Date=date_str,

        # conductor + resistance vs temp
        Tc=mot_c,
        Diameter=diameter_in,
        TLo=25.0, RLo=r25_ft,
        THi=50.0, RHi=r50_ft,
        ConductorsPerBundle=bundle
    )

    amps = Conductor(params).steady_state_thermal_rating()
    
    # Validate the result
    if amps is None or amps < 0 or not np.isfinite(amps):
        raise ValueError(f"Invalid IEEE 738 rating result: {amps}")
    
    return float(amps)


