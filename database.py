import aiosqlite
from datetime import datetime
from typing import List, Dict, Any

DATABASE_URL = "passwords.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL,
                numbers BOOLEAN NOT NULL,
                special BOOLEAN NOT NULL,
                uppercase BOOLEAN NOT NULL,
                capital BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def save_password(password: str, numbers: bool, special: bool, uppercase: bool, capital: bool):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "INSERT INTO passwords (password, numbers, special, uppercase, capital) VALUES (?, ?, ?, ?, ?)",
            (password, numbers, special, uppercase, capital)
        )
        await db.commit()

async def get_recent_passwords(limit: int = 50) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, password, numbers, special, uppercase, capital, created_at FROM passwords ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]