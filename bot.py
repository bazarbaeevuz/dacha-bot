import os
import gspread
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio

# ====== CONFIG ======
BOT_TOKEN = os.getenv("8537176060:AAHaAaTR3AJ3PAyL2080MhRCIMIjBF_UG3w")  # Telegram bot token
ADMIN_ID = 5523459970  # Sizning Telegram ID
GOOGLE_SHEET_URL = "1ewal_UpZ4M64Nk6Pa_L46Zwm0HYt--AUKRueBcY2H_Y"  # Google Sheet link (edit mumkin bo'lishi kerak)

# ====== Google Sheets Setup ======
# Faqat link orqali ochamiz
gc = gspread.service_account()  # JSON kerak emas, lekin Windowsda ishlash uchun "Anyone with link" Google Sheet
sheet = gc.open_by_url(GOOGLE_SHEET_URL).sheet1

# ====== Telegram Bot Setup ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== User States ======
user_data = {}

# ====== Helper: Bo‘sh sanalarni olish ======
def get_available_dates(dacha):
    all_rows = sheet.get_all_records()
    taken_dates = [row["Sana"] for row in all_rows if row["Dacha"] == dacha]
    from datetime import datetime, timedelta
    available = []
    for i in range(30):
        day = datetime.today() + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        if day_str not in taken_dates:
            available.append(day_str)
    return available

# ====== Commands ======
@dp.message(Command("start"))
async def start(message: types.Message):
    dacha_list = list(dict.fromkeys(sheet.col_values(2)[1:]))
    buttons = []
    for i in range(0, len(dacha_list), 2):
        row = [KeyboardButton(text=dacha_list[i])]
        if i + 1 < len(dacha_list):
            row.append(KeyboardButton(text=dacha_list[i+1]))
        buttons.append(row)
    dacha_kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Assalomu alaykum! Dachani tanlang:", reply_markup=dacha_kb)

# ====== Booking Flow ======
@dp.message()
async def booking(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # 1. Dacha tanlash
    if user_id not in user_data:
        user_data[user_id] = {"dacha": text}
        available_dates = get_available_dates(text)
        buttons = [[KeyboardButton(d)] for d in available_dates[:10]]
        date_kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Iltimos, bron qilish sanasini tanlang:", reply_markup=date_kb)
        return

    # 2. Sana tanlash
    if "sana" not in user_data[user_id]:
        user_data[user_id]["sana"] = text
        await message.answer("Iltimos, telefon raqamingizni kiriting:")
        return

    # 3. Telefon kiritish
    if "telefon" not in user_data[user_id]:
        user_data[user_id]["telefon"] = text
        dacha = user_data[user_id]["dacha"]
        sana = user_data[user_id]["sana"]
        telefon = user_data[user_id]["telefon"]
        ism = message.from_user.full_name

        # Google Sheets-ga yozish
        sheet.append_row([sana, dacha, ism, telefon, "kutilyapti", ""])

        # Adminga xabar
        await bot.send_message(ADMIN_ID, f"{ism} {dacha}ni {sana} sanaga bron qildi. Tel: {telefon}")

        await message.answer(f"Rahmat! Siz {dacha}ni {sana} sanaga bron qildingiz ✅")
        user_data.pop(user_id)
        return

# ====== Run ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
