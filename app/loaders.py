import pandas as pd
from .config import BUSES_CSV, LINES_CSV, COND_CSV

def load_all():
    buses = pd.read_csv(BUSES_CSV)
    lines = pd.read_csv(LINES_CSV)
    conds = pd.read_csv(COND_CSV)

    # normalize headers to lower-case
    buses.columns = [c.lower() for c in buses.columns]
    lines.columns = [c.lower() for c in lines.columns]
    conds.columns = [c.lower() for c in conds.columns]

    # expected columns based on your uploads
    # buses: name (int bus id), v_nom (kV), x (lon), y (lat), BusName
    # lines: name (L#), bus0, bus1, conductor, mot, s_nom, bus0_name, bus1_name
    # conds: conductorname, res_25c, res_50c, cdrad_in, cdgmr_ft
    return buses, lines, conds

def build_bus_lookup(buses: pd.DataFrame):
    # map bus id → (kv, lon, lat, name)
    buses = buses.rename(columns={"name":"bus_id", "v_nom":"kv", "x":"lon", "y":"lat"})
    return buses.set_index("bus_id")[["kv","lon","lat","busname"]].to_dict(orient="index")

def build_conductor_lookup(conds: pd.DataFrame):
    # Map '795 ACSR 26/7 DRAKE' → property dict
    conds = conds.rename(columns={
        "conductorname":"conductor",
        "res_25c":"res_25c_ohm_per_mile",
        "res_50c":"res_50c_ohm_per_mile",
        "cdrad_in":"diameter_in"
    })
    return conds.set_index("conductor").to_dict(orient="index")

