import sqlite3
import os
import re
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH")
DB_NAME = os.getenv("DB_NAME")

class Database:
    def __init__(self):
        self._ensure_table_exists()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _prepare_query(self, query: str) -> str:
        """Replace $1 style placeholders with SQLite compatible '?'"""
        return re.sub(r"\$\d+", "?", query)

    def _ensure_table_exists(self):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    discord_id TEXT PRIMARY KEY,
                    bday_day INTEGER NOT NULL CHECK (bday_day >= 1 AND bday_day <= 31),
                    bday_month INTEGER NOT NULL CHECK (bday_month >= 1 AND bday_month <= 12)
                )
            """)
            conn.commit()
            conn.close()
            print("[INFO] Database initialized and table ensured.")
        except Exception as e:
            print(f"[ERROR] Failed to initialize database: {e}")

    async def fetchrow(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(self._prepare_query(query), params)
            row = cursor.fetchone()
            conn.close()
            return row
        except Exception as e:
            print(f"[ERROR] fetchrow failed: {e}")
            return None

    async def fetch(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(self._prepare_query(query), params)
            rows = cursor.fetchall()
            conn.close()
            return [
                {"discord_id": r[0], "bday_day": r[1], "bday_month": r[2]} for r in rows
            ]
        except Exception as e:
            print(f"[ERROR] fetch failed: {e}")
            return []

    async def execute(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(self._prepare_query(query), params)
            conn.commit()
            conn.close()
            print("[INFO] Query executed successfully.")
        except Exception as e:
            print(f"[ERROR] Query execution failed: {e}")
