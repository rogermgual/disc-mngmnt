import logging
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH")
DB_NAME = os.getenv("DB_NAME")
logger = logging.getLogger("disc_bot")

class Database:
    def __init__(self):
        self._ensure_table_exists()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

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
            logger.info("Database initialized and table ensured.")
        except Exception as e:
            logger.error("Failed to initialize database: %s", e, exc_info=True)

    async def fetchrow(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query.replace("$1", "?").replace("$2", "?").replace("$3", "?"), params)
            row = cursor.fetchone()
            conn.close()
            return row
        except Exception as e:
            logger.error("fetchrow failed: %s", e, exc_info=True)
            return None

    async def fetch(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query.replace("$1", "?").replace("$2", "?").replace("$3", "?").replace("$4", "?"), params)
            rows = cursor.fetchall()
            conn.close()
            return [
                {"discord_id": r[0], "bday_day": r[1], "bday_month": r[2]} for r in rows
            ]
        except Exception as e:
            logger.error("fetch failed: %s", e, exc_info=True)
            return []

    async def execute(self, query, *params):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query.replace("$1", "?").replace("$2", "?").replace("$3", "?"), params)
            conn.commit()
            conn.close()
            logger.info("Query executed successfully.")
        except Exception as e:
            logger.error("Query execution failed: %s", e, exc_info=True)