from __future__ import annotations

from datetime import date, datetime, time, timedelta

import pandas as pd


DAY_NAMES = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "fr": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    "nl": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
}


def day_name_for_language(d: date, language: str = "en") -> str:
    names = DAY_NAMES.get(language, DAY_NAMES["en"])
    return names[d.weekday()]


def french_day_name(d: date) -> str:
    return day_name_for_language(d, "fr")


def compute_sleep_hours(sleep_t: time, wake_t: time) -> float:
    if sleep_t is None or wake_t is None:
        return 0.0
    today = date.today()
    dt_sleep = datetime.combine(today, sleep_t)
    dt_wake = datetime.combine(today, wake_t)
    if dt_wake <= dt_sleep:
        dt_wake += timedelta(days=1)
    delta = dt_wake - dt_sleep
    return round(delta.total_seconds() / 3600.0, 2)


def float_to_time_str(x):
    if pd.isna(x):
        return None
    try:
        x = float(x)
    except Exception:
        return None
    hours = int(x)
    minutes = int(round((x - hours) * 60))
    if minutes >= 60:
        hours += 1
        minutes -= 60
    hours = hours % 24
    return f"{hours:02d}:{minutes:02d}"
