# BT Tracker

Streamlit app for logging daily habits (hydration, nicotine, alcohol, sleep, running, weight) and monitoring progress through interactive charts. Data lives locally in SQLite, so you can import/export CSV snapshots without relying on external services.

## Features
- **Daily journal**: enter drinks, nicotine, social events, sleep schedule, sport activity, and weight in a single screen.
- **Automatic insights**: sleep duration calculated from bed/wake times, charts adapt their scales to highlight trends.
- **Graphs & history**: Altair-powered dashboards plus a sortable dataframe view for quick inspection.
- **CSV workflows**: import legacy spreadsheets or export the full dataset for backup/analysis.
- **Local-first storage**: SQLite file under `data/` created automatically; no extra infra required.

## Project Structure
```
bt_tracker/
├─ app.py               # Streamlit entry point (tabs, widgets, layout)
├─ requirements.txt     # Python dependencies
├─ core/
│  ├─ db.py             # SQLite helpers (init, CRUD)
│  ├─ utils.py          # Domain helpers (dates, sleep math, conversions)
│  ├─ import_export.py  # CSV ingestion logic
│  └─ charts.py         # Altair chart factories
├─ data/
│  └─ journal_bt.db     # SQLite database (auto-created)
└─ assets/
   └─ README.md         # Notes & ideas (optional)
```

## Getting Started
1. **Install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate on macOS/Linux
   pip install -r requirements.txt
   ```
2. **Run Streamlit**
   ```bash
   streamlit run app.py
   ```
3. Open the URL Streamlit prints (default `http://localhost:8501`).

The first run creates `data/journal_bt.db`. If you already have a DB from an earlier version, move it into `data/` before launching the app.

## Usage Tips
- **Daily entry**: Use the “Saisie du jour” tab. Existing entries are pre-filled if you revisit the same date.
- **Charts**: The “Graphiques” tab offers selectable liquid series and adaptive y-scales to highlight variations.
- **CSV import/export**: Head to “Historique”. Export dumps the current table. Import accepts CSV exports from Excel (headers listed in `core/import_export.py`), converts values, and upserts rows.
- **Data safety**: Backup `data/journal_bt.db` or the exported CSV periodically if you plan to reinstall or move machines.

## Development Notes
- Code style: simple functional modules under `core/` to keep Streamlit lean.
- Tests: not included yet; consider adding unit tests around `core/` functions for future contributions.
- Contributions: feel free to adapt the structure (more tabs, new metrics, etc.)—imports are centralized in `app.py`.

Enjoy tracking!

