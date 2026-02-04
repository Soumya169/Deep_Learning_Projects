# Deep_Learning_Projects

## Transportation Record App

A lightweight Flask app to collect transportation records from users and store them in SQLite for future analysis.

### Run locally

```bash
cd transport_app
python -m venv .venv
source .venv/bin/activate
pip install flask
python app.py
```

Then open `http://localhost:5000` in your browser.

### Deploy with Docker

```bash
cd transport_app
docker compose up --build
```

This publishes the app on `http://localhost:5000` and persists the SQLite database as `transport_records.db`.

### Export data

Use the **Download CSV** link on the home page to export all records for offline analysis.
