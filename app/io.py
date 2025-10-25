import pandas as pd
from .config import BUSES_CSV, LINES_CSV, COND_CSV, FLOWS_CSV

def load_buses() -> pd.DataFrame:
    df = pd.read_csv(BUSES_CSV)
    df.columns = [c.lower() for c in df.columns]
    # expected: name (bus id), v_nom (kV), optional busname
    return df

def load_lines() -> pd.DataFrame:
    df = pd.read_csv(LINES_CSV)
    df.columns = [c.lower() for c in df.columns]
    # expected: name(line id), bus0, bus1, conductor, mot, optional s_nom (MVA)
    return df

def load_conductors() -> pd.DataFrame:
    df = pd.read_csv(COND_CSV)
    df.columns = [c.lower() for c in df.columns]
    # normalize common column names
    rename = {
        "conductorname": "conductor",
        "res_25c": "res_25c_ohm_per_mile",
        "res_50c": "res_50c_ohm_per_mile",
        "cdrad_in": "diameter_in",   # some libs use cdrad_in
        "diameter": "diameter_in",
        "diameter_inch": "diameter_in",
        "conductorsperbundle": "conductors_per_bundle"
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "conductors_per_bundle" not in df.columns:
        df["conductors_per_bundle"] = 1
    return df


def load_flows() -> pd.DataFrame:
    df = pd.read_csv(FLOWS_CSV)
    df.columns = [c.lower() for c in df.columns]

    # Normalize ID
    if "name" in df.columns:
        df = df.rename(columns={"name": "line_id"})

    # Spec: p0_nominal is MVA
    if "p0_nominal" not in df.columns:
        raise ValueError("flows.csv must include 'p0_nominal' (MVA) column.")

    df["s_mva"] = df["p0_nominal"]
    df["profile"] = "nom"

    return df[["line_id", "profile", "s_mva"]]

