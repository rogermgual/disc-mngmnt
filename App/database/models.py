from database.db import Database

db = Database()

async def create_tables():
    await db.connect()
    await db.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id BIGINT PRIMARY KEY,
            birthday_date TEXT NOT NULL
        )
    ''')
    await db.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL,
            channel_id BIGINT NOT NULL,
            reminder_date TEXT NOT NULL,
            periodicity INT NOT NULL
        )
    ''')
    await db.execute('''
        CREATE TABLE IF NOT EXISTS raid_events (
            id SERIAL PRIMARY KEY,
            event_name TEXT NOT NULL,
            content_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            role_id BIGINT NOT NULL
        )
    ''')
    await db.close()