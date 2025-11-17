import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, time, timedelta

DB_PATH = "journal_bt.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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

    def parse_time(s):
        if s is None:
            return None
        try:
            return datetime.strptime(s, "%H:%M").time()
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


def upsert_entry(data: dict):
    conn = sqlite3.connect(DB_PATH)
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


def load_all():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM journal ORDER BY date", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def french_day_name(d: date) -> str:
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return jours[d.weekday()]


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

    new_cols = {}
    for col in df.columns:
        if col in col_map:
            new_cols[col] = col_map[col]
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

    for col in ["nico", "water_l", "beer_l", "alcool_cl", "wine_cl", "soda_l",
                "sleep_hours", "run_km", "weight"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["day_name"] = df["day_name"].astype(str)
    df.loc[df["day_name"].isin(["", "nan", "NaT"]), "day_name"] = df["date"].apply(french_day_name)

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
            "sleep_hours": float(row["sleep_hours"]) if not pd.isna(row["sleep_hours"]) else 0.0,
            "ran": int(row["ran"]) if not pd.isna(row["ran"]) else 0,
            "run_km": float(row["run_km"]) if not pd.isna(row["run_km"]) else 0.0,
            "weight": float(row["weight"]) if not pd.isna(row["weight"]) else None,
        }
        upsert_entry(data)
        count += 1

    return count


def main():
    st.set_page_config(page_title="Suivi BT", layout="wide")

    init_db()

    st.title("📊 Suivi journalier (version app du fichier Excel)")

    df = load_all()

    tab_saisie, tab_graphs, tab_histo = st.tabs(
        ["Saisie du jour", "Graphiques", "Historique"]
    )

    with tab_saisie:
        st.subheader("Saisie / édition d'une journée")

        col_date, col_day = st.columns([1, 1])
        with col_date:
            selected_date = st.date_input("Date", value=date.today())
        with col_day:
            st.write(" ")

        existing = load_entry(selected_date)
        day_name = french_day_name(selected_date)

        if existing:
            st.info(f"Données déjà existantes pour **{day_name} {selected_date}** (édition).")
        else:
            st.success(f"Nouvelle entrée pour **{day_name} {selected_date}**.")

        def dv(key, default):
            return existing.get(key) if existing and existing.get(key) is not None else default

        st.markdown("### Boissons & nicotine")
        c1, c2, c3 = st.columns(3)
        with c1:
            water_l = st.number_input("Eau (L / jour)", 0.0, 10.0, dv("water_l", 0.0), step=0.1)
            coffee = st.number_input("Cafés (tasses / jour)", 0, 30, dv("coffee", 0), step=1)
        with c2:
            beer_l = st.number_input("Bière (L / jour)", 0.0, 10.0, dv("beer_l", 0.0), step=0.1)
            alcool_cl = st.number_input("Alcool fort (cl / jour)", 0.0, 100.0, dv("alcool_cl", 0.0), step=1.0)
        with c3:
            wine_cl = st.number_input("Vin (cl / jour)", 0.0, 200.0, dv("wine_cl", 0.0), step=5.0)
            soda_l = st.number_input("Soda (L / jour)", 0.0, 10.0, dv("soda_l", 0.0), step=0.1)

        st.markdown("#### Nicotine / E-vape")
        nico = st.number_input(
            "%nico (mg/mL ou équivalent)",
            0.0,
            20.0,
            dv("nico", 3.17),
            step=0.01,
            format="%.2f",
        )

        st.markdown("### Soirée")
        c_soir1, c_soir2 = st.columns([1, 2])
        with c_soir1:
            soiree = st.checkbox("Soirée ?", value=dv("soiree", False))
        with c_soir2:
            soiree_name = st.text_input("Avec qui / où (N_soiree)", value=dv("soiree_name", "") or "")

        st.markdown("### Sommeil (Debout / Couchée / Sommeil)")
        c_sleep1, c_sleep2, c_sleep3 = st.columns(3)
        with c_sleep1:
            wake_default = dv("wake_time", time(6, 0))
            wake_time = st.time_input("Heure de lever", value=wake_default)
        with c_sleep2:
            sleep_default = dv("sleep_time", time(23, 0))
            sleep_time = st.time_input("Heure de coucher", value=sleep_default)
        with c_sleep3:
            sleep_hours = compute_sleep_hours(sleep_time, wake_time)
            st.metric("Heures de sommeil (V_somm)", f"{sleep_hours} h")

        st.markdown("### Sport (Courir)")
        c_run1, c_run2 = st.columns(2)
        with c_run1:
            ran = st.checkbox("Courir ?", value=dv("ran", False))
        with c_run2:
            run_km = st.number_input("Distance (km)", 0.0, 100.0, dv("run_km", 0.0), step=0.5)

        st.markdown("### Poids")
        weight = st.number_input("Poids (kg)", 0.0, 400.0, dv("weight", 0.0), step=0.1)

        if st.button("💾 Enregistrer / mettre à jour"):
            data = {
                "date": selected_date.isoformat(),
                "day_name": day_name,
                "nico": float(nico) if nico is not None else None,
                "water_l": float(water_l),
                "coffee": int(coffee),
                "beer_l": float(beer_l),
                "alcool_cl": float(alcool_cl),
                "wine_cl": float(wine_cl),
                "soda_l": float(soda_l),
                "soiree": int(soiree),
                "soiree_name": soiree_name if soiree else None,
                "wake_time": wake_time.strftime("%H:%M") if wake_time else None,
                "sleep_time": sleep_time.strftime("%H:%M") if sleep_time else None,
                "sleep_hours": float(sleep_hours),
                "ran": int(ran),
                "run_km": float(run_km),
                "weight": float(weight) if weight else None,
            }
            upsert_entry(data)
            st.success("Données enregistrées ✅")

    with tab_graphs:
        st.subheader("Graphiques")

        if df.empty:
            st.info("Pas encore de données enregistrées.")
        else:
            df_sorted = df.sort_values("date").set_index("date")

            st.markdown("#### Poids (kg)")
            df_weight = df_sorted.dropna(subset=["weight"])
            if not df_weight.empty:
                st.line_chart(df_weight["weight"])
            else:
                st.write("Pas encore de poids saisis.")

            st.markdown("#### Sommeil (heures par nuit)")
            st.line_chart(df_sorted["sleep_hours"])

            st.markdown("#### Nicotine (`%nico`)")
            st.line_chart(df_sorted["nico"])

            st.markdown("#### Course (km)")
            st.line_chart(df_sorted["run_km"])

            st.markdown("#### Consommation de liquides")

            liquid_options = {
                "Eau (L)": "water_l",
                "Bière (L)": "beer_l",
                "Vin (cl)": "wine_cl",
                "Alcool fort (cl)": "alcool_cl",
                "Soda (L)": "soda_l",
            }

            selected_liquids = st.multiselect(
                "Liquides à afficher",
                list(liquid_options.keys()),
                default=list(liquid_options.keys()),
            )

            if selected_liquids:
                cols = [liquid_options[label] for label in selected_liquids]
                df_liquids = df_sorted[cols]
                st.line_chart(df_liquids)
            else:
                st.info("Sélectionne au moins un liquide pour afficher le graphique.")

    with tab_histo:
        st.subheader("Historique détaillé")

        st.markdown("### Export des données")
        if df.empty:
            st.info("Pas encore de données enregistrées, rien à exporter.")
        else:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Exporter les données en CSV",
                data=csv_data,
                file_name="journal_bt.csv",
                mime="text/csv",
            )

        st.markdown("---")

        st.markdown("### Import depuis un CSV (Excel ou export de l'app)")
        uploaded_file = st.file_uploader(
            "Choisis un fichier CSV à importer",
            type=["csv"],
            help="Tu peux exporter ton onglet DB_DATA_SCADA en CSV depuis Excel, puis l'importer ici.",
        )

        if uploaded_file is not None:
            try:
                n = import_csv_to_db(uploaded_file)
                st.success(f"{n} lignes importées / mises à jour avec succès ✅")
            except Exception as e:
                st.error(f"Erreur lors de l'import : {e}")

        st.markdown("---")

        df = load_all()
        if df.empty:
            st.info("Pas encore de données enregistrées.")
        else:
            df_view = df[
                [
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
                    "sleep_hours",
                    "ran",
                    "run_km",
                    "weight",
                ]
            ].sort_values("date")

            st.dataframe(df_view, use_container_width=True)


if __name__ == "__main__":
    main()
