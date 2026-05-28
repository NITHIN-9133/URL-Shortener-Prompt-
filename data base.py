import sqlite3
import random
import string
from datetime import datetime

DB_PATH = "urls.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT    NOT NULL UNIQUE,
            original   TEXT    NOT NULL,
            clicks     INTEGER NOT NULL DEFAULT 0,
            created_at TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def shorten_url(original_url: str, custom_code: str = None) -> dict:
    conn = get_connection()
    try:
        if custom_code:
            code = custom_code
        else:
            for _ in range(10):
                code = generate_code()
                if not conn.execute("SELECT code FROM urls WHERE code = ?", (code,)).fetchone():
                    break
            else:
                return {"error": "Could not generate a unique code. Try again."}

        if conn.execute("SELECT code FROM urls WHERE code = ?", (code,)).fetchone():
            return {"error": f"Code '{code}' is already taken."}

        created_at = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT INTO urls (code, original, created_at) VALUES (?, ?, ?)",
            (code, original_url, created_at),
        )
        conn.commit()
        return {"code": code, "original": original_url, "created_at": created_at}
    finally:
        conn.close()


def get_url(code: str) -> str | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT original FROM urls WHERE code = ?", (code,)).fetchone()
        if row:
            conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
            conn.commit()
            return row["original"]
        return None
    finally:
        conn.close()


def get_all_urls() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT code, original, clicks, created_at FROM urls ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_url(code: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM urls WHERE code = ?", (code,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()