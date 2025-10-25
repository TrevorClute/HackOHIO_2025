import pandas as pd
import numpy as np
from .physics_ieee import ieee738_rating_amps_from_rows, amps_to_mva, mva_to_amps

def _build_bus_lookup(buses: pd.DataFrame):
    out = {}
    for _, r in buses.iterrows():
        bid = int(r["name"])
        kv = float(r.get("v_nom", r.get("kv", np.nan)))
        busname = str(r["busname"]) if "busname" in buses.columns and pd.notna(r["busname"]) else f"BUS_{bid}"
        out[bid] = {"kv": kv, "busname": busname}
    return out

def _build_cond_lookup(conds: pd.DataFrame):
    if "conductor" not in conds.columns:
        return {}
    return conds.set_index("conductor").to_dict(orient="index")

def compute_stress_table(buses_df, lines_df, conds_df, flows_df,
                         ambient_c: float, wind_ms: float, wind_angle_deg: float,
                         warn_threshold: float, bad_threshold: float) -> pd.DataFrame:
    BUS = _build_bus_lookup(buses_df)
    COND = _build_cond_lookup(conds_df)

    # Use ONLY s_mva (apparent power) from flows
    flows = flows_df[flows_df["profile"] == "nom"].set_index("line_id")
    if "s_mva" not in flows.columns:
        raise ValueError("Internal: flows_df must contain 's_mva' column. Check app/io.py::load_flows().")

    rows = []
    for _, L in lines_df.iterrows():
        lid = str(L["name"])
        if lid not in flows.index:
            continue

        s_val = flows.loc[lid, "s_mva"]
        if pd.isna(s_val):
            continue
        s_mva = float(s_val)

        b0 = int(L["bus0"]); b1 = int(L["bus1"])
        if b0 not in BUS:
            continue
        kv = float(BUS[b0]["kv"])

        cond_name = str(L.get("conductor", ""))
        if cond_name not in COND:
            continue
        cond_row = COND[cond_name]

        mot_c = float(L.get("mot", 80.0))

        # 1) dynamic rating via IEEE-738 (A -> MVA)
        rating_a = ieee738_rating_amps_from_rows(cond_row, mot_c, ambient_c, wind_ms, wind_angle_deg)
        rating_mva = amps_to_mva(rating_a, kv)

        # 2) actual flow: S (MVA) -> A
        flow_mva = s_mva
        flow_a = mva_to_amps(flow_mva, kv)

        # 3) utilization & status
        util = (flow_a / rating_a) * 100.0 if rating_a > 0 else float("inf")
        if util > bad_threshold:
            status, overloaded = "BAD", True
        elif util >= warn_threshold:
            status, overloaded = "WARN", False
        else:
            status, overloaded = "GOOD", False

        rows.append({
            "line_id": lid,
            "bus0": b0, "bus1": b1,
            "bus0_name": BUS[b0]["busname"],
            "bus1_name": BUS.get(b1, {}).get("busname"),
            "conductor": cond_name,
            "voltage_kv": kv,
            "mot_c": mot_c,

            "rating_amps": float(rating_a),
            "rating_mva": float(rating_mva),
            "flow_amps": float(flow_a),
            "flow_mva": float(flow_mva),

            "utilization_pct": float(util),
            "status": status,
            "overloaded": overloaded,

            "ampacity_margin_a": float(rating_a - flow_a),
            "mva_margin": float(rating_mva - flow_mva),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("utilization_pct", ascending=False)
    return df

