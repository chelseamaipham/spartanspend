"""
Loads sample_expenses.csv into the SpartanSpend database.
The dates are shifted into the current month so the Dashboard has data to show.

Run with:  python load_sample.py
"""

import csv
import sqlite3
from datetime import date

DB_PATH = "spartanspend.db"

conn = sqlite3.connect(DB_PATH)
conn.execute(
    """CREATE TABLE IF NOT EXISTS expenses (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           date TEXT NOT NULL,
           description TEXT NOT NULL,
           category TEXT NOT NULL,
           amount REAL NOT NULL
       )"""
)

today = date.today()
count = 0
with open("sample_expenses.csv", newline="") as f:
    for row in csv.DictReader(f):
        day = min(int(row["day"]), today.day)
        expense_date = date(today.year, today.month, day)
        conn.execute(
            "INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)",
            (expense_date.isoformat(), row["description"], row["category"], float(row["amount"])),
        )
        count += 1

conn.commit()
conn.close()
print(f"Loaded {count} sample expenses.")