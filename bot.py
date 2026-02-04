import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8537176060:AAHaAaTR3AJ3PAyL2080MhRCIMIjBF_UG3w"
ADMIN_ID = 5523459970  # admin telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Tugmalar
dacha_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏡 Dacha №1"), KeyboardButton(text="🏡 Dacha №2")],
        [KeyboardButton(text="🏡 Dacha №3"), KeyboardButton(text="🏡 Dacha №4")],
        [KeyboardButton(text="📞 Admin bilan bog‘lanish")]
    ],
    resize_keyboard=True
)

user_data = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum 👋\nDachani tanlang:",
        reply_markup=dacha_kb
    )

@dp.message(lambda m: "Dacha" in m.text)
async def choose_dacha(message: types.Message):
    user_data[message.from_user.id] = {"dacha": message.text}
    await message.answer("📅 Qaysi sana? (masalan: 12.02.2026)")

@dp.message(lambda m: m.text.count(".") == 2)
async def choose_date(message: types.Message):
    data = user_data.get(message.from_user.id)
    if not data:
        return

    data["sana"] = message.text

    text = (
        f"📩 YANGI SO‘ROV\n\n"
        f"👤 Mijoz: {message.from_user.full_name}\n"
        f"📞 Username: @{message.from_user.username}\n"
        f"{data['dacha']}\n"
        f"📅 Sana: {data['sana']}"
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer(
        "✅ So‘rov yuborildi.\nAdmin siz bilan bog‘lanadi."
    )

@dp.message(lambda m: "Admin" in m.text)
async def admin_contact(message: types.Message):
    await message.answer("☎️ Admin: +998 xx xxx xx xx")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
