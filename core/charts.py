from __future__ import annotations

import altair as alt
import pandas as pd


def make_dynamic_line_chart(df: pd.DataFrame, y_col: str, y_label: str):
    s = df[y_col].dropna()
    s = s[s != 0]
    if s.empty:
        return None
    ymin = s.min()
    ymax = s.max()
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    padding = (ymax - ymin) * 0.1
    domain = (ymin - padding, ymax + padding)
    chart = (
        alt.Chart(df.reset_index())
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(f"{y_col}:Q", title=y_label, scale=alt.Scale(domain=domain)),
            tooltip=["date:T", alt.Tooltip(f"{y_col}:Q", title=y_label)],
        )
        .properties(height=300)
    )
    return chart


def make_basic_line_chart(df: pd.DataFrame, y_col: str, y_label: str):
    s = df[y_col].dropna()
    if s.empty:
        return None
    chart = (
        alt.Chart(df.reset_index())
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(f"{y_col}:Q", title=y_label),
            tooltip=["date:T", alt.Tooltip(f"{y_col}:Q", title=y_label)],
        )
        .properties(height=300)
    )
    return chart


def make_liquids_chart(df_sorted: pd.DataFrame, cols, label_map):
    df_liquids = df_sorted[cols]
    df_melt = df_liquids.reset_index().melt("date", var_name="type", value_name="value")
    df_melt = df_melt.dropna(subset=["value"])
    if df_melt.empty:
        return None
    df_melt["type"] = df_melt["type"].map(label_map)
    chart = (
        alt.Chart(df_melt)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Quantité"),
            color=alt.Color("type:N", title="Liquide"),
            tooltip=["date:T", "type:N", "value:Q"],
        )
        .properties(height=300)
    )
    return chart

