import numpy as np

def line_azimuth_deg(lon0, lat0, lon1, lat1):
    """Rough azimuth (deg) from bus0 → bus1. Only used if you later want wind angle per-line."""
    # Simple equirect approximation good enough for visualization
    dlon = (lon1 - lon0) * np.cos(np.deg2rad((lat0 + lat1) / 2.0))
    dlat = (lat1 - lat0)
    ang = np.rad2deg(np.arctan2(dlon, dlat)) % 360.0
    return ang

