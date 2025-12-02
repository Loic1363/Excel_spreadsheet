from __future__ import annotations

import pandas as pd

from .db import upsert_entry
from .utils import french_day_name, float_to_time_str


def import_csv_to_db(file) -> int:
    df = pd.read_csv(file, engine="python", sep=None)

    col_map = {
        "Temps": "date",
        "V_jour": "day_name",
        "%nico": "nico",
        "L_eau": "water_l",
        "T_coffee": "coffee",
        "L_bière": "beer_l",
        "L_biere": "beer_l",
        "cl_alcool": "alcool_cl",
        "cl_vin": "wine_cl",
        "L_soda": "soda_l",
        "B_soiree": "soiree",
        "N_soiree": "soiree_name",
        "V_debout": "wake_time",
        "V_couche": "sleep_time",
        "V_somm": "sleep_hours",
        "B_courrir": "ran",
        "V_courrir": "run_km",
        "V_poids": "weight",
        "date": "date",
        "day_name": "day_name",
        "nico": "nico",
        "water_l": "water_l",
        "coffee": "coffee",
        "beer_l": "beer_l",
        "alcool_cl": "alcool_cl",
        "wine_cl": "wine_cl",
        "soda_l": "soda_l",
        "soiree": "soiree",
        "soiree_name": "soiree_name",
        "wake_time": "wake_time",
        "sleep_time": "sleep_time",
        "sleep_hours": "sleep_hours",
        "ran": "ran",
        "run_km": "run_km",
        "weight": "weight",
    }

    new_cols = {col: col_map[col] for col in df.columns if col in col_map}
    df = df.rename(columns=new_cols)

    wanted_cols = [
        "date",
        "day_name",
        "nico",
        "water_l",
        "coffee",
        "beer_l",
        "alcool_cl",
        "wine_cl",
        "soda_l",
        "soiree",
        "soiree_name",
        "wake_time",
        "sleep_time",
        "sleep_hours",
        "ran",
        "run_km",
        "weight",
    ]
    for c in wanted_cols:
        if c not in df.columns:
            df[c] = None

    if df["date"].isna().all():
        raise ValueError("Aucune colonne 'date' ou 'Temps' valide trouvée dans le CSV.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True).dt.date
    df = df.dropna(subset=["date"])

    if df["wake_time"].dtype != "object":
        df["wake_time"] = df["wake_time"].apply(float_to_time_str)
    else:
        df["wake_time"] = df["wake_time"].astype(str).where(df["wake_time"].notna(), None)

    if df["sleep_time"].dtype != "object":
        df["sleep_time"] = df["sleep_time"].apply(float_to_time_str)
    else:
        df["sleep_time"] = df["sleep_time"].astype(str).where(df["sleep_time"].notna(), None)

    df["soiree"] = df["soiree"].fillna(0).astype(int)
    df["ran"] = df["ran"].fillna(0).astype(int)
    df["coffee"] = df["coffee"].fillna(0).astype(int)

    for col in [
        "nico",
        "water_l",
        "beer_l",
        "alcool_cl",
        "wine_cl",
        "soda_l",
        "sleep_hours",
        "run_km",
        "weight",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["day_name"] = df["day_name"].astype(str)
    df.loc[df["day_name"].isin(["", "nan", "NaT"]), "day_name"] = df["date"].apply(
        french_day_name
    )

    count = 0
    for _, row in df.iterrows():
        data = {
            "date": row["date"].isoformat(),
            "day_name": row["day_name"],
            "nico": float(row["nico"]) if not pd.isna(row["nico"]) else None,
            "water_l": float(row["water_l"]) if not pd.isna(row["water_l"]) else 0.0,
            "coffee": int(row["coffee"]) if not pd.isna(row["coffee"]) else 0,
            "beer_l": float(row["beer_l"]) if not pd.isna(row["beer_l"]) else 0.0,
            "alcool_cl": float(row["alcool_cl"]) if not pd.isna(row["alcool_cl"]) else 0.0,
            "wine_cl": float(row["wine_cl"]) if not pd.isna(row["wine_cl"]) else 0.0,
            "soda_l": float(row["soda_l"]) if not pd.isna(row["soda_l"]) else 0.0,
            "soiree": int(row["soiree"]) if not pd.isna(row["soiree"]) else 0,
            "soiree_name": row["soiree_name"] if pd.notna(row["soiree_name"]) else None,
            "wake_time": row["wake_time"] if pd.notna(row["wake_time"]) else None,
            "sleep_time": row["sleep_time"] if pd.notna(row["sleep_time"]) else None,
            "sleep_hours": (
                float(row["sleep_hours"]) if not pd.isna(row["sleep_hours"]) else 0.0
            ),
            "ran": int(row["ran"]) if not pd.isna(row["ran"]) else 0,
            "run_km": float(row["run_km"]) if not pd.isna(row["run_km"]) else 0.0,
            "weight": float(row["weight"]) if not pd.isna(row["weight"]) else None,
        }
        upsert_entry(data)
        count += 1

    return count

