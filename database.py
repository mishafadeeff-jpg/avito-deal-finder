import aiosqlite
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "avito_finder.db")

async def init_db():
    """Инициализация базы данных объявлений и пользователей."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица подписок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                plan_key TEXT,
                expire_at TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Таблица уже отсканированных объявлений (для защиты от дублей)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scanned_items (
                item_id TEXT PRIMARY KEY,
                title TEXT,
                price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def check_vip_status(user_id: int) -> bool:
    """Проверяет VIP-подписку перекупа."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT expire_at, is_active FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            expire_str, is_active = row
            if not is_active:
                return False
            expire_at = datetime.datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
            return datetime.datetime.now() < expire_at

async def save_scanned_item(item_id: str, title: str, price: int) -> bool:
    """Сохраняет объявление. Возвращает True, если объявление новое."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO scanned_items (item_id, title, price) VALUES (?, ?, ?)",
                (item_id, title, price)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False # Уже было отправлено
