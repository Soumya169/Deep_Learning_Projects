from __future__ import annotations

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "transport_records.db"

app = Flask(__name__)
app.secret_key = "transport-records-secret"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transportation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                mode TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                distance_km REAL NOT NULL,
                cost REAL NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


init_db()


@app.route("/")
def index() -> str:
    with get_connection() as connection:
        records = connection.execute(
            """
            SELECT id, user_name, travel_date, mode, origin, destination, distance_km, cost, notes
            FROM transportation_records
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()
    return render_template("index.html", records=records)


@app.route("/submit", methods=["POST"])
def submit() -> Response:
    form = request.form
    required_fields = [
        "user_name",
        "travel_date",
        "mode",
        "origin",
        "destination",
        "distance_km",
        "cost",
    ]

    missing_fields = [field for field in required_fields if not form.get(field)]
    if missing_fields:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("index"))

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO transportation_records (
                user_name, travel_date, mode, origin, destination, distance_km, cost, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            ,
            (
                form["user_name"].strip(),
                form["travel_date"].strip(),
                form["mode"].strip(),
                form["origin"].strip(),
                form["destination"].strip(),
                float(form["distance_km"]),
                float(form["cost"]),
                form.get("notes", "").strip(),
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )

    flash("Transportation record saved.", "success")
    return redirect(url_for("index"))


@app.route("/records")
def records() -> str:
    with get_connection() as connection:
        records = connection.execute(
            """
            SELECT id, user_name, travel_date, mode, origin, destination, distance_km, cost, notes, created_at
            FROM transportation_records
            ORDER BY id DESC
            """
        ).fetchall()
    return render_template("records.html", records=records)


@app.route("/export")
def export_csv() -> Response:
    with get_connection() as connection:
        records = connection.execute(
            """
            SELECT id, user_name, travel_date, mode, origin, destination, distance_km, cost, notes, created_at
            FROM transportation_records
            ORDER BY id DESC
            """
        ).fetchall()

    def generate() -> str:
        output = csv.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "user_name",
                "travel_date",
                "mode",
                "origin",
                "destination",
                "distance_km",
                "cost",
                "notes",
                "created_at",
            ]
        )
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)
        for record in records:
            writer.writerow(
                [
                    record["id"],
                    record["user_name"],
                    record["travel_date"],
                    record["mode"],
                    record["origin"],
                    record["destination"],
                    record["distance_km"],
                    record["cost"],
                    record["notes"],
                    record["created_at"],
                ]
            )
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    headers = {"Content-Disposition": "attachment; filename=transportation_records.csv"}
    return Response(generate(), mimetype="text/csv", headers=headers)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
