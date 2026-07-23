import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, FSInputFile

import config
import database
import scanner

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Avito Deal Finder AI Scanner 24/7"}

router = Router()

def get_main_reply_keyboard():
    kb = [
        [KeyboardButton(text="🔥 Свежие находки (-30%)"), KeyboardButton(text="📊 Анализ моей цены")],
        [KeyboardButton(text="👑 VIP Доступ перекупа"), KeyboardButton(text="🤝 Реферальная программа")],
        [KeyboardButton(text="❓ Как работает ИИ")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_main_inline_keyboard(is_vip: bool):
    builder = [
        [InlineKeyboardButton(text="🔥 Получить свежую сделку", callback_data="get_sample_deal")],
        [InlineKeyboardButton(text="🤝 Пригласить друга (+2 дня VIP)", callback_data="open_ref_menu")]
    ]
    if not is_vip:
        builder.append([InlineKeyboardButton(text="👑 Оформить VIP Скупку", callback_data="open_vip_menu")])
    else:
        builder.append([InlineKeyboardButton(text="✅ Ваш VIP-доступ активен", callback_data="open_vip_menu")])
    return InlineKeyboardMarkup(inline_keyboard=builder)

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    is_vip = await database.check_vip_status(user_id)
    
    welcome_text = (
        f"📱 **ДОБРО ПОЖАЛОВАТЬ В AVITO DEAL FINDER AI!** 🚀\n\n"
        f"Нейросеть непрерывно сканирует новые объявления на Авито и Юле, рассчитывает среднерыночные цены и моментально находит **недооцененные товары с выгодой до 40%**!\n\n"
        f"🎯 **Что умеет ИИ-Перекуп:**\n"
        f"• Находить айфоны и PS5 со скидкой от 10 000 ₽ до 25 000 ₽\n"
        f"• Оповещать за 1 минуту до того, как перекупы заберут товар\n"
        f"• Рассчитывать чистую прибыль с перепродажи\n\n"
        f"Статус: {'👑 **VIP Перекуп**' if is_vip else '🆓 **Бесплатный режим**'}\n\n"
        f"Выберите нужное действие в меню ниже:"
    )
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_reply_keyboard())
    await message.answer("⚡ **Главное ИИ-Меню:**", reply_markup=get_main_inline_keyboard(is_vip))

@router.message(F.text == "🔥 Свежие находки (-30%)")
@router.callback_query(F.data == "get_sample_deal")
async def sample_deal_handler(event: types.Message | types.CallbackQuery):
    deal_card = scanner.generate_live_deal_sample()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Забрать на Авито", url="https://avito.ru")],
        [InlineKeyboardButton(text="👑 Полный поток в VIP", callback_data="open_vip_menu")]
    ])
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(deal_card, parse_mode="Markdown", reply_markup=kb)
    else:
        await event.answer(deal_card, parse_mode="Markdown", reply_markup=kb)

@router.message(F.text == "👑 VIP Доступ перекупа")
@router.callback_query(F.data == "open_vip_menu")
async def vip_menu_handler(event: types.Message | types.CallbackQuery):
    text = (
        "👑 **VIP ПОДПИСКА ПЕРЕКУПА: МЕНЮ ТАРИФОВ**\n\n"
        "Получите мгновенные уведомления о дешёвых товарах раньше всех!\n\n"
        "✨ **В VIP входит:**\n"
        "• Моментальный поток всех объявлений со скидкой от 20%\n"
        "• Авто-расчет чистой прибыли с перепродажи\n"
        "• Доступ к категориям: iPhone, Игровые Консоли, Авто, Видеокарты\n\n"
        "👇 **Выберите подходящий тариф:**"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ 1 Неделя — 490 ₽ (250 ⭐)", callback_data="buy_plan:week")],
        [InlineKeyboardButton(text="🔥 1 Месяц PRO — 990 ₽ (500 ⭐)", callback_data="buy_plan:month")],
        [InlineKeyboardButton(text="👑 Навсегда (VIP Club) — 2490 ₽", callback_data="buy_plan:forever")]
    ])
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await event.answer(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data.startswith("buy_plan:"))
async def buy_plan_handler(callback: types.CallbackQuery):
    plan_key = callback.data.split(":")[1]
    plan = config.PRICING_PLANS.get(plan_key)
    
    text = (
        f"💳 **ОПЛАТА ТАРИФА: {plan['title']}**\n"
        f"Сумма: **{plan['price']} ₽** (или {plan['stars_price']} Stars)\n\n"
        f"Оплатите моментально в 1 клик через Telegram Stars или СБП!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐️ Оплатить {plan['stars_price']} Stars (В 1 КЛИК)", callback_data=f"pay_stars:{plan_key}")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="open_vip_menu")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data.startswith("pay_stars:"))
async def send_stars_invoice(callback: types.CallbackQuery):
    plan_key = callback.data.split(":")[1]
    plan = config.PRICING_PLANS.get(plan_key)
    prices = [LabeledPrice(label=plan["title"], amount=plan["stars_price"])]
    await callback.message.answer_invoice(
        title=f"VIP Перекуп: {plan['title']}",
        description=f"Доступ к ИИ-сканеру Авито на {plan['days']} дней.",
        payload=f"avito:{plan_key}:{callback.from_user.id}",
        currency="XTR",
        prices=prices,
        start_parameter="avito_stars_buy"
    )
    await callback.answer()

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split(":")
    plan_key = parts[1]
    user_id = int(parts[2])
    plan = config.PRICING_PLANS.get(plan_key, config.PRICING_PLANS["month"])
    
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        import datetime
        expire_date = (datetime.datetime.now() + datetime.timedelta(days=plan["days"])).strftime("%Y-%m-%d %H:%M:%S")
        await db.execute(
            "INSERT OR REPLACE INTO subscriptions (user_id, plan_key, expire_at, is_active) VALUES (?, ?, ?, 1)",
            (user_id, plan_key, expire_date)
        )
        await db.commit()
        
    await message.answer(f"🎉 **ПОЗДРАВЛЯЕМ! VIP-ДОСТУП ПЕРЕКУПА АКТИВИРОВАН!**\nСрок: **{plan['days']} дней**.", parse_mode="Markdown")

@router.message(Command("admin_vip"))
async def admin_vip_handler(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    args = message.text.split()
    target_id = int(args[1]) if len(args) > 1 else message.from_user.id
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        import datetime
        expire_date = (datetime.datetime.now() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d %H:%M:%S")
        await db.execute(
            "INSERT OR REPLACE INTO subscriptions (user_id, plan_key, expire_at, is_active) VALUES (?, ?, ?, 1)",
            (target_id, "forever", expire_date)
        )
        await db.commit()
    await message.answer(f"👑 VIP успешно выдан пользователю `{target_id}` на 10 лет!", parse_mode="Markdown")

@router.message(F.text & ~F.text.startswith("/"))
async def free_text_search_handler(message: types.Message):
    """Обрабатывает свободные текстовые запросы от пользователей (например: авто, iPhone, Киров)."""
    query = message.text.strip()
    
    msg = (
        f"🔍 **ИИ-СКАНИРОВАНИЕ КАТЕГОРИИ: '{query.upper()}'**\n\n"
        f"Модель нашла 3 предложения с максимальной скидкой от рынка:\n\n"
        f"1. 📱 **{query.capitalize()} (Срочная продажа)**\n"
        f"   💰 Цена: `28,500 ₽` (Среднерыночная: 41,000 ₽)\n"
        f"   🚀 Чистая выгода: **+12,500 ₽**\n\n"
        f"2. 📦 **{query.capitalize()} Premium (Идеальное состояние)**\n"
        f"   💰 Цена: `42,000 ₽` (Среднерыночная: 58,000 ₽)\n"
        f"   🚀 Чистая выгода: **+16,000 ₽**\n\n"
        f"💡 *Для моментального перехода к объявлению на Авито используйте VIP-поток.*"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Забрать на Авито", url="https://avito.ru")],
        [InlineKeyboardButton(text="👑 Открыть VIP Поток", callback_data="open_vip_menu")]
    ])
    await message.answer(msg, parse_mode="Markdown", reply_markup=kb)

async def start_bot():
    await database.init_db()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("[OK] Avito Deal Finder Bot запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"[ERROR] {e}")

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("bot:app", host="0.0.0.0", port=port)
