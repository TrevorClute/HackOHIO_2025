import sys
from pathlib import Path
import numpy as np
from .config import (
    OHM_PER_MILE_TO_OHM_PER_FT, MS_TO_FPS,
    DEFAULT_WIND_ANGLE, DEFAULT_SUN_HOUR, DEFAULT_ELEVATION_FT, DEFAULT_LATITUDE_DEG,
    DEFAULT_EMISSIVITY, DEFAULT_ABSORPTIVITY, DEFAULT_ATMOSPHERE, DEFAULT_DIRECTION
)

# import your ieee738 module from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import ieee738  # ← your uploaded file
from ieee738 import ConductorParams, Conductor

def amps_to_mva(i_a: float, kv: float) -> float:
    # S(MVA) = √3 * I(A) * V(kV)
    return float(np.sqrt(3.0) * i_a * kv * 1e-3)

def compute_line_ampacity(
    line_row: dict,
    bus0_kv: float,
    conductor_lib_row: dict,
    ambient_c: float,
    wind_ms: float,
    wind_angle_deg: float = DEFAULT_WIND_ANGLE,
    sun_hour: float = DEFAULT_SUN_HOUR,
    elevation_ft: float = DEFAULT_ELEVATION_FT,
    latitude_deg: float = DEFAULT_LATITUDE_DEG,
    emissivity: float = DEFAULT_EMISSIVITY,
    absorptivity: float = DEFAULT_ABSORPTIVITY,
    atmosphere: str = DEFAULT_ATMOSPHERE,
    direction: str = DEFAULT_DIRECTION
) -> float:
    """
    Returns ampacity (A) for the line under the given ambient & wind.
    """
    # Required per your ieee738.ConductorParams:
    #  - Ta (°C), WindVelocity (ft/s), WindAngleDeg, SunTime, Elevation(ft), Latitude(deg),
    #  - Emissivity, Absorptivity, Atmosphere, Direction
    #  - Tc (MOT °C), Diameter(in), TLo(°C), RLo(ohm/ft), THi(°C), RHi(ohm/ft)
    wind_fps = wind_ms * MS_TO_FPS

    # Line-specified MOT (°C)
    mot_c = float(line_row.get("mot", 80.0))

    # Conductor library mapping (ohm/mile → ohm/ft)
    r25_ohm_per_ft = float(conductor_lib_row["res_25c_ohm_per_mile"]) * OHM_PER_MILE_TO_OHM_PER_FT
    r50_ohm_per_ft = float(conductor_lib_row["res_50c_ohm_per_mile"]) * OHM_PER_MILE_TO_OHM_PER_FT
    diameter_in     = float(conductor_lib_row["diameter_in"])

    cp = ConductorParams(
        # ambient
        Ta=ambient_c,
        WindVelocity=wind_fps,
        WindAngleDeg=wind_angle_deg,
        SunTime=sun_hour,
        Elevation=elevation_ft,
        Latitude=latitude_deg,
        Emissivity=emissivity,
        Absorptivity=absorptivity,
        Atmosphere=atmosphere,
        Direction=direction,
        # conductor / electrical
        Tc=mot_c,
        Diameter=diameter_in,
        TLo=25.0,   RLo=r25_ohm_per_ft,
        THi=50.0,   RHi=r50_ohm_per_ft,
        ConductorsPerBundle=int(line_row.get("conductorsperbundle", 1))
    )
    con = Conductor(cp)
    amps = con.steady_state_thermal_rating()
    return float(amps)

