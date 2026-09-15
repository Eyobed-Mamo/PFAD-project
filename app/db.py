"""
SQLite persistence layer for the dashboard.

Kept deliberately simple (single table) since the analytics are computed
with pandas after reading the table back out -- SQL here is for storage,
dedup, and multi-session persistence, not heavy aggregation.
"""
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "finance.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_batch TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    category_source TEXT NOT NULL,
    month TEXT NOT NULL
);
"""

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn

def insert_transactions(df: pd.DataFrame, batch_id: str):
    conn = get_connection()
    df = df.copy()
    df["upload_batch"] = batch_id
    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

def load_all_transactions() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transactions", conn, parse_dates=["date"])
    conn.close()
    return df

def clear_all():
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

def list_batches():
    conn = get_connection()
    batches = pd.read_sql(
        "SELECT upload_batch, COUNT(*) as n, MIN(date) as start, MAX(date) as end "
        "FROM transactions GROUP BY upload_batch ORDER BY MAX(date) DESC",
        conn
    )
    conn.close()
    return batches
