import streamlit as st
from datetime import date, time

from core.charts import (
    make_basic_line_chart,
    make_dynamic_line_chart,
    make_liquids_chart,
)
from core.db import init_db, load_all, load_entry, upsert_entry
from core.import_export import import_csv_to_db
from core.utils import compute_sleep_hours, day_name_for_language

LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
    ("nl", "Nederlands"),
]
LANGUAGE_LABELS = {
    "en": "Language",
    "fr": "Langue",
    "nl": "Taal",
}
LANGUAGE_NAME_MAP = {code: name for code, name in LANGUAGES}
LANGUAGE_WIDGET_KEY = "language_selector"

TRANSLATIONS = {
    "app_title": {
        "en": "〆 Daily Journal",
        "fr": "〆 Suivi journalier",
        "nl": "〆 Dagelijks logboek",
    },
    "entry_tab": {"en": "Daily Entry", "fr": "Saisie du jour", "nl": "Dagelijkse invoer"},
    "graphs_tab": {"en": "Charts", "fr": "Graphiques", "nl": "Grafieken"},
    "history_tab": {"en": "History", "fr": "Historique", "nl": "Historiek"},
    "entry_subheader": {
        "en": "Enter / edit a day",
        "fr": "Saisie / édition d'une journée",
        "nl": "Dag invullen / bewerken",
    },
    "date_label": {"en": "Date", "fr": "Date", "nl": "Datum"},
    "existing_entry": {
        "en": "Data already exists for **{day_name} {date}** (editing).",
        "fr": "Données déjà existantes pour **{day_name} {date}** (édition).",
        "nl": "Gegevens bestaan al voor **{day_name} {date}** (bewerking).",
    },
    "new_entry": {
        "en": "New entry for **{day_name} {date}**.",
        "fr": "Nouvelle entrée pour **{day_name} {date}**.",
        "nl": "Nieuwe invoer voor **{day_name} {date}**.",
    },
    "section_drinks": {
        "en": "Drinks & nicotine",
        "fr": "Boissons & nicotine",
        "nl": "Dranken & nicotine",
    },
    "water_input": {
        "en": "Water (L / day)",
        "fr": "Eau (L / jour)",
        "nl": "Water (L / dag)",
    },
    "coffee_input": {
        "en": "Coffee (cups / day)",
        "fr": "Cafés (tasses / jour)",
        "nl": "Koffie (tassen / dag)",
    },
    "beer_input": {
        "en": "Beer (L / day)",
        "fr": "Bière (L / jour)",
        "nl": "Bier (L / dag)",
    },
    "alcohol_input": {
        "en": "Spirits (cl / day)",
        "fr": "Alcool fort (cl / jour)",
        "nl": "Sterke drank (cl / dag)",
    },
    "wine_input": {
        "en": "Wine (cl / day)",
        "fr": "Vin (cl / jour)",
        "nl": "Wijn (cl / dag)",
    },
    "soda_input": {
        "en": "Soda (L / day)",
        "fr": "Soda (L / jour)",
        "nl": "Frisdrank (L / dag)",
    },
    "section_nicotine": {
        "en": "Nicotine / E-vape",
        "fr": "Nicotine / E-vape",
        "nl": "Nicotine / e-vape",
    },
    "nico_input": {
        "en": "%nico (mg/mL or equivalent)",
        "fr": "%nico (mg/mL ou équivalent)",
        "nl": "%nico (mg/mL of equivalent)",
    },
    "section_party": {
        "en": "Evening",
        "fr": "Soirée",
        "nl": "Avond",
    },
    "party_checkbox": {
        "en": "Night out?",
        "fr": "Soirée ?",
        "nl": "Uitstapje?",
    },
    "party_name": {
        "en": "With whom / where",
        "fr": "Avec qui / où (N_soiree)",
        "nl": "Met wie / waar",
    },
    "section_sleep": {
        "en": "Sleep (wake / bed / duration)",
        "fr": "Sommeil (Debout / Couchée / Sommeil)",
        "nl": "Slaap (opstaan / naar bed / duur)",
    },
    "wake_label": {
        "en": "Wake-up time",
        "fr": "Heure de lever",
        "nl": "Opstaan uur",
    },
    "sleep_label": {
        "en": "Bedtime",
        "fr": "Heure de coucher",
        "nl": "Slaaptijd",
    },
    "sleep_metric": {
        "en": "Sleep hours",
        "fr": "Heures de sommeil (V_somm)",
        "nl": "Slaapuren",
    },
    "section_run": {
        "en": "Running",
        "fr": "Sport (Courir)",
        "nl": "Sport (lopen)",
    },
    "ran_checkbox": {"en": "Run?", "fr": "Courir ?", "nl": "Gelopen?"},
    "run_distance": {"en": "Distance (km)", "fr": "Distance (km)", "nl": "Afstand (km)"},
    "section_weight": {"en": "Weight", "fr": "Poids", "nl": "Gewicht"},
    "weight_input": {"en": "Weight (kg)", "fr": "Poids (kg)", "nl": "Gewicht (kg)"},
    "save_button": {
        "en": "💾 Save / update",
        "fr": "💾 Enregistrer / mettre à jour",
        "nl": "💾 Opslaan / bijwerken",
    },
    "save_success": {
        "en": "Data saved ✅",
        "fr": "Données enregistrées ✅",
        "nl": "Gegevens opgeslagen ✅",
    },
    "graphs_subheader": {"en": "Charts", "fr": "Graphiques", "nl": "Grafieken"},
    "no_data_info": {
        "en": "No data recorded yet.",
        "fr": "Pas encore de données enregistrées.",
        "nl": "Nog geen gegevens geregistreerd.",
    },
    "weight_chart_title": {
        "en": "Weight (kg)",
        "fr": "Poids (kg)",
        "nl": "Gewicht (kg)",
    },
    "weight_chart_info": {
        "en": "No useful weight data (all zero or empty).",
        "fr": "Pas de données de poids utiles (toutes à 0 ou vides).",
        "nl": "Geen bruikbare gewichtgegevens (alles nul of leeg).",
    },
    "sleep_chart_title": {
        "en": "Sleep (hours per night)",
        "fr": "Sommeil (heures par nuit)",
        "nl": "Slaap (uren per nacht)",
    },
    "sleep_chart_info": {
        "en": "No useful sleep data.",
        "fr": "Pas de données de sommeil utiles.",
        "nl": "Geen bruikbare slaapgegevens.",
    },
    "nico_chart_title": {
        "en": "Nicotine (`%nico`)",
        "fr": "Nicotine (`%nico`)",
        "nl": "Nicotine (`%nico`)",
    },
    "nico_chart_info": {
        "en": "No useful nicotine data.",
        "fr": "Pas de données de nicotine utiles.",
        "nl": "Geen bruikbare nicotinegegevens.",
    },
    "run_chart_title": {
        "en": "Running (km)",
        "fr": "Course (km)",
        "nl": "Lopen (km)",
    },
    "run_chart_info": {
        "en": "No useful running data.",
        "fr": "Pas de données de course utiles.",
        "nl": "Geen bruikbare loopgegevens.",
    },
    "liquids_section": {
        "en": "Liquid consumption",
        "fr": "Consommation de liquides",
        "nl": "Vloeistofconsumptie",
    },
    "liquid_select": {
        "en": "Liquids to display",
        "fr": "Liquides à afficher",
        "nl": "Te tonen vloeistoffen",
    },
    "liquid_info_empty": {
        "en": "Select at least one liquid to display the chart.",
        "fr": "Sélectionne au moins un liquide pour afficher le graphique.",
        "nl": "Selecteer minstens één vloeistof om de grafiek te tonen.",
    },
    "liquid_no_data": {
        "en": "No useful liquid data (all empty).",
        "fr": "Pas de données de liquides utiles (toutes vides).",
        "nl": "Geen bruikbare vloeistofgegevens (alles leeg).",
    },
    "history_subheader": {
        "en": "Detailed history",
        "fr": "Historique détaillé",
        "nl": "Gedetailleerde historiek",
    },
    "export_section": {
        "en": "Data export",
        "fr": "Export des données",
        "nl": "Gegevens export",
    },
    "export_info": {
        "en": "No data recorded yet, nothing to export.",
        "fr": "Pas encore de données enregistrées, rien à exporter.",
        "nl": "Nog geen gegevens geregistreerd, niets om te exporteren.",
    },
    "export_button": {
        "en": "📥 Export data to CSV",
        "fr": "📥 Exporter les données en CSV",
        "nl": "📥 Gegevens exporteren naar CSV",
    },
    "import_section": {
        "en": "Import from CSV (Excel or app export)",
        "fr": "Import depuis un CSV (Excel ou export de l'app)",
        "nl": "Importeer vanuit CSV (Excel of app-export)",
    },
    "weight_axis": {
        "en": "Weight (kg)",
        "fr": "Poids (kg)",
        "nl": "Gewicht (kg)",
    },
    "sleep_axis": {
        "en": "Sleep (h)",
        "fr": "Sommeil (h)",
        "nl": "Slaap (u)",
    },
    "nico_axis": {
        "en": "%nico",
        "fr": "%nico",
        "nl": "%nico",
    },
    "run_axis": {
        "en": "Running (km)",
        "fr": "Course (km)",
        "nl": "Lopen (km)",
    },
    "import_label": {
        "en": "Choose a CSV file to import",
        "fr": "Choisis un fichier CSV à importer",
        "nl": "Kies een CSV-bestand om te importeren",
    },
    "import_help": {
        "en": "Export your DB_DATA_SCADA sheet from Excel as CSV, then import it here.",
        "fr": "Tu peux exporter ton onglet DB_DATA_SCADA en CSV depuis Excel, puis l'importer ici.",
        "nl": "Exporteer je DB_DATA_SCADA-blad uit Excel naar CSV en importeer het hier.",
    },
    "import_success": {
        "en": "{rows} rows imported/updated successfully ✅",
        "fr": "{rows} lignes importées / mises à jour avec succès ✅",
        "nl": "{rows} rijen succesvol geimporteerd/bijgewerkt ✅",
    },
    "import_error": {
        "en": "Import error: {error}",
        "fr": "Erreur lors de l'import : {error}",
        "nl": "Importfout: {error}",
    },
}

LIQUID_FIELDS = ["water_l", "beer_l", "wine_cl", "alcool_cl", "soda_l"]

LIQUID_LABELS = {
    "water_l": {"en": "Water (L)", "fr": "Eau (L)", "nl": "Water (L)"},
    "beer_l": {"en": "Beer (L)", "fr": "Bière (L)", "nl": "Bier (L)"},
    "wine_cl": {"en": "Wine (cl)", "fr": "Vin (cl)", "nl": "Wijn (cl)"},
    "alcool_cl": {"en": "Spirits (cl)", "fr": "Alcool fort (cl)", "nl": "Sterke drank (cl)"},
    "soda_l": {"en": "Soda (L)", "fr": "Soda (L)", "nl": "Frisdrank (L)"},
}


def select_language_code() -> str:
    if LANGUAGE_WIDGET_KEY not in st.session_state:
        st.session_state[LANGUAGE_WIDGET_KEY] = "en"
    current_code = st.session_state[LANGUAGE_WIDGET_KEY]
    label = LANGUAGE_LABELS.get(current_code, LANGUAGE_LABELS["en"])
    options = [code for code, _ in LANGUAGES]
    selected_code = st.sidebar.selectbox(
        label,
        options,
        format_func=lambda code: LANGUAGE_NAME_MAP[code],
        key=LANGUAGE_WIDGET_KEY,
    )
    return selected_code


def main():
    st.set_page_config(page_title="Suivi BT", layout="wide")

    language_code = select_language_code()
    t = lambda key, **kwargs: TRANSLATIONS[key][language_code].format(**kwargs)

    init_db()

    st.title(t("app_title"))

    df = load_all()

    tab_saisie, tab_graphs, tab_histo = st.tabs(
        [t("entry_tab"), t("graphs_tab"), t("history_tab")]
    )

    with tab_saisie:
        st.subheader(t("entry_subheader"))

        col_date, col_day = st.columns([1, 1])
        with col_date:
            selected_date = st.date_input(t("date_label"), value=date.today())
        with col_day:
            st.write(" ")

        existing = load_entry(selected_date)
        day_name = day_name_for_language(selected_date, language_code)

        if existing:
            st.info(t("existing_entry", day_name=day_name, date=selected_date))
        else:
            st.success(t("new_entry", day_name=day_name, date=selected_date))

        def dv(key, default):
            return existing.get(key) if existing and existing.get(key) is not None else default

        st.markdown(f"### {t('section_drinks')}")
        c1, c2, c3 = st.columns(3)
        with c1:
            water_l = st.number_input(t("water_input"), 0.0, 10.0, dv("water_l", 0.0), step=0.1)
            coffee = st.number_input(t("coffee_input"), 0, 30, dv("coffee", 0), step=1)
        with c2:
            beer_l = st.number_input(t("beer_input"), 0.0, 10.0, dv("beer_l", 0.0), step=0.1)
            alcool_cl = st.number_input(
                t("alcohol_input"), 0.0, 100.0, dv("alcool_cl", 0.0), step=1.0
            )
        with c3:
            wine_cl = st.number_input(t("wine_input"), 0.0, 200.0, dv("wine_cl", 0.0), step=5.0)
            soda_l = st.number_input(t("soda_input"), 0.0, 10.0, dv("soda_l", 0.0), step=0.1)

        st.markdown(f"#### {t('section_nicotine')}")
        nico = st.number_input(
            t("nico_input"),
            0.0,
            20.0,
            dv("nico", 3.17),
            step=0.01,
            format="%.2f",
        )

        st.markdown(f"### {t('section_party')}")
        c_soir1, c_soir2 = st.columns([1, 2])
        with c_soir1:
            soiree = st.checkbox(t("party_checkbox"), value=dv("soiree", False))
        with c_soir2:
            soiree_name = st.text_input(t("party_name"), value=dv("soiree_name", "") or "")

        st.markdown(f"### {t('section_sleep')}")
        c_sleep1, c_sleep2, c_sleep3 = st.columns(3)
        with c_sleep1:
            wake_default = dv("wake_time", time(6, 0))
            wake_time = st.time_input(t("wake_label"), value=wake_default)
        with c_sleep2:
            sleep_default = dv("sleep_time", time(23, 0))
            sleep_time = st.time_input(t("sleep_label"), value=sleep_default)
        with c_sleep3:
            sleep_hours = compute_sleep_hours(sleep_time, wake_time)
            st.metric(t("sleep_metric"), f"{sleep_hours} h")

        st.markdown(f"### {t('section_run')}")
        c_run1, c_run2 = st.columns(2)
        with c_run1:
            ran = st.checkbox(t("ran_checkbox"), value=dv("ran", False))
        with c_run2:
            run_km = st.number_input(t("run_distance"), 0.0, 100.0, dv("run_km", 0.0), step=0.5)

        st.markdown(f"### {t('section_weight')}")
        weight = st.number_input(t("weight_input"), 0.0, 400.0, dv("weight", 0.0), step=0.1)

        if st.button(t("save_button")):
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
            st.success(t("save_success"))

    with tab_graphs:
        st.subheader(t("graphs_subheader"))

        if df.empty:
            st.info(t("no_data_info"))
        else:
            df_sorted = df.sort_values("date").set_index("date")

            st.markdown(f"#### {t('weight_chart_title')}")
            chart_weight = make_dynamic_line_chart(df_sorted, "weight", t("weight_axis"))
            if chart_weight is not None:
                st.altair_chart(chart_weight, use_container_width=True)
            else:
                st.write(t("weight_chart_info"))

            st.markdown(f"#### {t('sleep_chart_title')}")
            chart_sleep = make_dynamic_line_chart(df_sorted, "sleep_hours", t("sleep_axis"))
            if chart_sleep is not None:
                st.altair_chart(chart_sleep, use_container_width=True)
            else:
                st.write(t("sleep_chart_info"))

            st.markdown(f"#### {t('nico_chart_title')}")
            chart_nico = make_basic_line_chart(df_sorted, "nico", t("nico_axis"))
            if chart_nico is not None:
                st.altair_chart(chart_nico, use_container_width=True)
            else:
                st.write(t("nico_chart_info"))

            st.markdown(f"#### {t('run_chart_title')}")
            chart_run = make_basic_line_chart(df_sorted, "run_km", t("run_axis"))
            if chart_run is not None:
                st.altair_chart(chart_run, use_container_width=True)
            else:
                st.write(t("run_chart_info"))

            st.markdown(f"#### {t('liquids_section')}")

            liquid_options = {
                LIQUID_LABELS[field][language_code]: field for field in LIQUID_FIELDS
            }
            reverse_label = {v: k for k, v in liquid_options.items()}

            selected_liquids = st.multiselect(
                t("liquid_select"),
                list(liquid_options.keys()),
                default=list(liquid_options.keys()),
            )

            if selected_liquids:
                cols = [liquid_options[label] for label in selected_liquids]
                chart_liquids = make_liquids_chart(df_sorted, cols, reverse_label)
                if chart_liquids is not None:
                    st.altair_chart(chart_liquids, use_container_width=True)
                else:
                    st.info(t("liquid_no_data"))
            else:
                st.info(t("liquid_info_empty"))

    with tab_histo:
        st.subheader(t("history_subheader"))

        st.markdown(f"### {t('export_section')}")
        if df.empty:
            st.info(t("export_info"))
        else:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=t("export_button"),
                data=csv_data,
                file_name="journal_bt.csv",
                mime="text/csv",
            )

        st.markdown("---")

        st.markdown(f"### {t('import_section')}")
        uploaded_file = st.file_uploader(
            t("import_label"),
            type=["csv"],
            help=t("import_help"),
        )

        if uploaded_file is not None:
            try:
                n = import_csv_to_db(uploaded_file)
                st.success(t("import_success", rows=n))
            except Exception as e:
                st.error(t("import_error", error=e))

        st.markdown("---")

        df = load_all()
        if df.empty:
            st.info(t("no_data_info"))
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
            df_view = df_view.copy()
            df_view["day_name"] = df_view["date"].apply(
                lambda d: day_name_for_language(d, language_code)
            )

            st.dataframe(df_view, use_container_width=True)


if __name__ == "__main__":
    main()
