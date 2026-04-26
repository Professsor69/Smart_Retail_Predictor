"""
db_connection.py
----------------
Central database connection module for Smart Retail Predictor.
"""

import os
import time
import mysql.connector
from mysql.connector import pooling, Error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Configuration ─────────────────────────────────────────────────────────────
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_CONFIG = {
    "host":     DB_HOST,
    "user":     os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Kushagra"),    # ← Default local password
    "database": os.environ.get("DB_NAME", "smart_retail_db"),
    "port":     int(os.environ.get("DB_PORT", 3306)),
    "charset":  "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
    "connection_timeout": 10,
    "use_pure": True,
}

# TiDB Cloud requires SSL. We disable strict CA verification for simplicity on Windows.
if "tidbcloud" in DB_HOST.lower():
    DB_CONFIG["ssl_disabled"] = False
    DB_CONFIG["ssl_verify_cert"] = False

# ── Simple connection ─────────────────────────────────────────────────────────
def get_db_connection(retries: int = 3, delay: float = 1.0):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                return conn
        except Error as e:
            last_error = e
            if attempt < retries:
                time.sleep(delay)
    raise ConnectionError(f"Could not connect to MySQL. Error: {last_error}")

# ── Dictionary-cursor shortcut ────────────────────────────────────────────────
def get_cursor(conn):
    return conn.cursor(dictionary=True)

# ── Health-check utility ──────────────────────────────────────────────────────
def ping() -> bool:
    try:
        conn = get_db_connection(retries=1)
        conn.close()
        return True
    except Exception:
        return False

# ── Safe query helpers ────────────────────────────────────────────────────────
def execute_query(sql: str, params: tuple = (), fetch: bool = False):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    finally:
        cursor.close()
        conn.close()

def execute_many(sql: str, data: list):
    conn = get_db_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        cursor.executemany(sql, data)
        conn.commit()
        return cursor.rowcount
    except Error:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.autocommit = True
        conn.close()