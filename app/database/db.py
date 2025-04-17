import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST'),
            port=os.getenv("DB_PORT")
        )

    #Close the connection
    async def close(self):
        if self.conn and not self.conn.is_closed():
            await self.conn.close()

    #Execute a query (INSERT, UPDATE, DELETE) and return the result
    async def execute(self, query, *args):
        await self.connect()
        return await self.conn.execute(query, *args)

    #Execute a query (SELECT) and return the result
    async def fetch(self, query, *args):
        await self.connect()
        return await self.conn.fetch(query, *args)
    
    #Execute a query (SELECT) and return a single row
    async def fetchrow(self, query, *args):
            await self.connect()
            return await self.conn.fetchrow(query, *args)

    #Execute a query (SELECT) and return a single value
    async def fetchval(self, query, *args):
        await self.connect()
        return await self.conn.fetchval(query, *args)
