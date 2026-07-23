import random
import datetime

# Среднерыночные ориентиры цен на электронику для ИИ-оценки скидки
MARKET_PRICES = {
    "iPhone 11": 22000,
    "iPhone 12": 32000,
    "iPhone 13": 44000,
    "iPhone 14": 56000,
    "iPhone 15": 69000,
    "PlayStation 5": 42000,
    "RTX 3060": 24000,
    "RTX 4060": 31000
}

def analyze_deal(title: str, seller_price: int) -> dict | None:
    """
    ИИ-Аналитик цен. Проверяет, насколько объявление выгоднее рынка.
    Если скидка больше 20%, возвращает структуру сделки.
    """
    for model_name, avg_market_price in MARKET_PRICES.items():
        if model_name.lower() in title.lower():
            if seller_price < avg_market_price * 0.85: # Скидка от 15% и выше
                discount_amount = avg_market_price - seller_price
                discount_percent = int((discount_amount / avg_market_price) * 100)
                
                return {
                    "model": model_name,
                    "title": title,
                    "seller_price": seller_price,
                    "market_price": avg_market_price,
                    "profit": discount_amount,
                    "discount_percent": discount_percent
                }
    return None

def generate_live_deal_sample() -> str:
    """Генерирует тестовую горячую сделку для демонстрации."""
    deals = [
        ("iPhone 13 128GB Синий (Отличное состояние)", 31000, 44000),
        ("PlayStation 5 Disc Edition (2 геймпада)", 31500, 42000),
        ("iPhone 14 Pro 256GB Космос", 49000, 68000),
        ("Видеокарта RTX 3060 Ti 8GB", 18500, 26000)
    ]
    title, price, market = random.choice(deals)
    profit = market - price
    percent = int((profit / market) * 100)
    
    card = (
        f"🔥 **ГОРЯЧЕЕ ОБЪЯВЛЕНИЕ (-{percent}% ОТ РЫНКА)** 🔥\n\n"
        f"📱 **Товар:** {title}\n"
        f"💰 **Цена продавца:** `{price:,} ₽`\n"
        f"📊 **Средняя цена рынка:** ~{market:,} ₽\n"
        f"🚀 **Чистая прибыль перекупа:** **+{profit:,} ₽**\n\n"
        f"📍 Город: Москва / СПб (Срочная продажа)\n"
        f"⏳ Выложено: только что (1 мин назад)\n\n"
        f"💡 *Успейте забрать первыми по кнопке ниже!*"
    )
    return card
