from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "journal_bt.db"


def get_conn() -> sqlite3.Connection:
    """Return a SQLite connection, ensuring the data directory exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS journal (
            date TEXT PRIMARY KEY,
            day_name TEXT,
            nico REAL,
            water_l REAL,
            coffee INT,
            beer_l REAL,
            alcool_cl REAL,
            wine_cl REAL,
            soda_l REAL,
            soiree INTEGER,
            soiree_name TEXT,
            wake_time TEXT,
            sleep_time TEXT,
            sleep_hours REAL,
            ran INTEGER,
            run_km REAL,
            weight REAL
        )
        """
    )
    conn.commit()
    conn.close()


def load_entry(d: date):
    """Load a single entry, returning convenient python types for the UI."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM journal WHERE date = ?", (d.isoformat(),))
    row = c.fetchone()
    conn.close()
    if not row:
        return None

    (
        date_str,
        day_name,
        nico,
        water_l,
        coffee,
        beer_l,
        alcool_cl,
        wine_cl,
        soda_l,
        soiree,
        soiree_name,
        wake_time,
        sleep_time,
        sleep_hours,
        ran,
        run_km,
        weight,
    ) = row

    def parse_time(value: str | None) -> time | None:
        if value is None:
            return None
        try:
            return datetime.strptime(value, "%H:%M").time()
        except Exception:
            return None

    return {
        "date": datetime.fromisoformat(date_str).date(),
        "day_name": day_name,
        "nico": nico,
        "water_l": water_l,
        "coffee": coffee,
        "beer_l": beer_l,
        "alcool_cl": alcool_cl,
        "wine_cl": wine_cl,
        "soda_l": soda_l,
        "soiree": bool(soiree),
        "soiree_name": soiree_name,
        "wake_time": parse_time(wake_time),
        "sleep_time": parse_time(sleep_time),
        "sleep_hours": sleep_hours,
        "ran": bool(ran),
        "run_km": run_km,
        "weight": weight,
    }


def upsert_entry(data: dict) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO journal (
            date, day_name, nico, water_l, coffee, beer_l,
            alcool_cl, wine_cl, soda_l,
            soiree, soiree_name,
            wake_time, sleep_time, sleep_hours,
            ran, run_km, weight
        ) VALUES (
            :date, :day_name, :nico, :water_l, :coffee, :beer_l,
            :alcool_cl, :wine_cl, :soda_l,
            :soiree, :soiree_name,
            :wake_time, :sleep_time, :sleep_hours,
            :ran, :run_km, :weight
        )
        ON CONFLICT(date) DO UPDATE SET
            day_name = excluded.day_name,
            nico = excluded.nico,
            water_l = excluded.water_l,
            coffee = excluded.coffee,
            beer_l = excluded.beer_l,
            alcool_cl = excluded.alcool_cl,
            wine_cl = excluded.wine_cl,
            soda_l = excluded.soda_l,
            soiree = excluded.soiree,
            soiree_name = excluded.soiree_name,
            wake_time = excluded.wake_time,
            sleep_time = excluded.sleep_time,
            sleep_hours = excluded.sleep_hours,
            ran = excluded.ran,
            run_km = excluded.run_km,
            weight = excluded.weight
        """,
        data,
    )
    conn.commit()
    conn.close()


def load_all() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM journal ORDER BY date", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

