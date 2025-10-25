from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))

# CSVs you uploaded
BUSES_CSV  = Path(os.getenv("BUSES_CSV",  DATA_DIR / "buses.csv"))
LINES_CSV  = Path(os.getenv("LINES_CSV",  DATA_DIR / "lines.csv"))
COND_CSV   = Path(os.getenv("COND_CSV",   DATA_DIR / "conductor_library.csv"))

# Defaults for rating calc
DEFAULT_AMBIENT_C   = float(os.getenv("DEFAULT_AMBIENT_C", 30.0))
DEFAULT_WIND_MS     = float(os.getenv("DEFAULT_WIND_MS", 2.0))   # m/s (we convert to ft/s for ieee module)
DEFAULT_WIND_ANGLE  = float(os.getenv("DEFAULT_WIND_ANGLE", 90)) # deg (90 = perpendicular)
DEFAULT_SUN_HOUR    = float(os.getenv("DEFAULT_SUN_HOUR", 12))   # hour in [0..24]
DEFAULT_ELEVATION_FT= float(os.getenv("DEFAULT_ELEVATION_FT", 0))
DEFAULT_LATITUDE_DEG= float(os.getenv("DEFAULT_LATITUDE_DEG", 21.3))
DEFAULT_EMISSIVITY  = float(os.getenv("DEFAULT_EMISSIVITY", 0.5))
DEFAULT_ABSORPTIVITY= float(os.getenv("DEFAULT_ABSORPTIVITY", 0.5))
DEFAULT_ATMOSPHERE  = os.getenv("DEFAULT_ATMOSPHERE", "Clear")
DEFAULT_DIRECTION   = os.getenv("DEFAULT_DIRECTION", "EastWest") # used only for solar term

# Units
OHM_PER_MILE_TO_OHM_PER_FT = 1.0 / 5280.0
MS_TO_FPS = 3.280839895013123

