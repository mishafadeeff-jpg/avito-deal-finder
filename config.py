import os
from dotenv import load_dotenv

load_dotenv()

# Токен нового бота (можно будет легко указать из BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8735864553:AAEsRYbBajptKOV8B1y19kYz0lz8RcVuS9s")

# Админы (твой Telegram ID)
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "860392517").split(",") if id_str.strip()]

# Тарифы для перекупов
PRICING_PLANS = {
    "week": {
        "title": "⚡ 1 Неделя Тест",
        "days": 7,
        "price": 490,
        "stars_price": 250,
        "description": "7 дней моментальных уведомлений о дешёвых товарах"
    },
    "month": {
        "title": "🔥 1 Месяц Перекуп PRO",
        "days": 30,
        "price": 990,
        "stars_price": 500,
        "description": "30 дней полного доступа к сканеру Авито"
    },
    "forever": {
        "title": "👑 Навсегда (VIP Скупка)",
        "days": 3658,
        "price": 2490,
        "stars_price": 1250,
        "description": "Безлимитный пожизненный доступ ко всем категориям"
    }
}
