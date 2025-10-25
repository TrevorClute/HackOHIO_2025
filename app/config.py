from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))

# Path to your line geometry GeoJSON (server-side)
GIS_LINES_GEOJSON = Path(
    os.getenv("GIS_LINES_GEOJSON",
              "./data/oneline_lines.geojson")  # set this to your real path
)

# input files
BUSES_CSV  = Path(os.getenv("BUSES_CSV",  DATA_DIR / "buses.csv"))
LINES_CSV  = Path(os.getenv("LINES_CSV",  DATA_DIR / "lines.csv"))
COND_CSV   = Path(os.getenv("COND_CSV",   DATA_DIR / "conductor_library.csv"))
FLOWS_CSV  = Path(os.getenv("FLOWS_CSV",  DATA_DIR / "flows.csv"))  # name,p0_nominal

# weather defaults (override via query params or env)
DEFAULT_AMBIENT_C = float(os.getenv("DEFAULT_AMBIENT_C", 35.0))
DEFAULT_WIND_MS   = float(os.getenv("DEFAULT_WIND_MS",   1.0))
DEFAULT_WIND_ANGLE_DEG = float(os.getenv("DEFAULT_WIND_ANGLE_DEG", 90.0))  # perpendicular

# solar & environment defaults (used by ieee738)
ELEVATION_FT = float(os.getenv("ELEVATION_FT", 0.0))
LATITUDE_DEG = float(os.getenv("LATITUDE_DEG", 21.3))  # Hawaii default
SUNTIME_HR   = float(os.getenv("SUNTIME_HR", 12.0))    # local solar noon
EMISSIVITY   = float(os.getenv("EMISSIVITY", 0.5))
ABSORPTIVITY = float(os.getenv("ABSORPTIVITY", 0.5))
DIRECTION    = os.getenv("DIRECTION", "EastWest")
ATMOSPHERE   = os.getenv("ATMOSPHERE", "Clear")
DATE_STR     = os.getenv("DATE_STR", "12 Jun")         # format like '12 Jun'

# status thresholds
WARN_THRESHOLD = float(os.getenv("WARN_THRESHOLD", 80.0))   # %
BAD_THRESHOLD  = float(os.getenv("BAD_THRESHOLD",  100.0))  # %

# units
MS_TO_FPS = 3.280839895013123  # m/s → ft/s
MILES_TO_FEET = 5280.0

