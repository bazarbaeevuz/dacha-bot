import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8537176060:AAFwjKqKsWccmtzdbDPAn337X9P8apznc6s"
ADMIN_ID = 5523459970  # o'zingizning Telegram ID
SHEET_ID = "1oDsLVUtInYy7_12TD_J9LRInhPvINCpDxzmVz6HhTYY"  # Google Sheet ID (URL dan)
JSON_PATH = "google_credentials.json"  # bot.py bilan bir papkada bo'lsin

DACHALAR = ["🏡 Dacha 1", "🏠 Dacha 2", "🌴 Dacha 3"]


# ===================== GOOGLE SHEETS =====================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1


# ===================== BOT =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}  # vaqtincha bron jarayoni


# ===================== HELPERS =====================
def norm(x) -> str:
    return str(x).strip()


def is_date_busy(dacha: str, sana: str) -> bool:
    """Holat = bekor bo'lmagan bo'lsa shu sana band hisoblanadi."""
    rows = sheet.get_all_records()
    for row in rows:
        if (
            norm(row.get("Dacha", "")) == norm(dacha)
            and norm(row.get("Sana", "")) == norm(sana)
            and norm(row.get("Holat", "")).lower() != "bekor"
        ):
            return True
    return False


def append_booking(sana: str, dacha: str, ism: str, telefon: str, user_id: int) -> int:
    """Bronni sheetga qo'shadi, qaytargani: qo'shilgan qator raqami (row index)."""
    sheet.append_row([
        sana, dacha, ism, telefon,
        "kutilyapti",  # Holat
        "",            # AdminMsgId
        str(user_id)   # UserId
    ])
    return len(sheet.get_all_values())  # oxirgi qator index


def set_admin_msg_id(row_index: int, msg_id: int):
    # AdminMsgId = F ustun (6)
    sheet.update_cell(row_index, 6, str(msg_id))


def update_status(row_index: int, status: str):
    # Holat = E ustun (5)
    sheet.update_cell(row_index, 5, status)


def find_row_by_admin_msg_id(admin_msg_id: int):
    """Admin xabari message_id bo'yicha sheet qatorini topamiz."""
    rows = sheet.get_all_records()
    for i, row in enumerate(rows, start=2):  # 1-qator header, data 2-dan
        if norm(row.get("AdminMsgId", "")) == str(admin_msg_id):
            return i, row
    return None, None


# ===================== /start =====================
@dp.message(Command("start"))
async def start(message: types.Message):
    user_data.pop(message.from_user.id, None)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=d)] for d in DACHALAR],
        resize_keyboard=True
    )
    await message.answer("🏡 Dachani tanlang:", reply_markup=kb)


# ===================== /jadval (admin) =====================
@dp.message(Command("jadval"))
async def jadval(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = sheet.get_all_records()
    active = [r for r in rows if norm(r.get("Holat", "")).lower() != "bekor"]

    if not active:
        await message.answer("📭 Hozircha faol bron yo‘q.")
        return

    lines = ["📋 Faol bronlar (20 tagacha):"]
    for r in active[:20]:
        lines.append(
            f"• {r.get('Sana')} | {r.get('Dacha')} | {r.get('Ism')} | {r.get('Telefon')} | {r.get('Holat')}"
        )
    await message.answer("\n".join(lines))


# ===================== Bron flow =====================
@dp.message()
async def booking(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()

    # 1) Dacha
    if uid not in user_data:
        if text not in DACHALAR:
            await message.answer("❗ Dachani tugmadan tanlang.")
            return
        user_data[uid] = {"dacha": text}
        await message.answer("📅 Sanani kiriting (YYYY-MM-DD):")
        return

    # 2) Sana
    if "sana" not in user_data[uid]:
        sana = text
        dacha = user_data[uid]["dacha"]

        # format tekshiruv
        try:
            datetime.strptime(sana, "%Y-%m-%d")
        except:
            await message.answer("❗ Sana formati xato. Masalan: 2026-02-10")
            return

        # band tekshiruv
        if is_date_busy(dacha, sana):
            await message.answer("❌ Bu sana band. Iltimos boshqa sanani tanlang.")
            user_data.pop(uid, None)
            return

        user_data[uid]["sana"] = sana
        await message.answer("📞 Telefon raqamingizni kiriting:")
        return

    # 3) Telefon => sheetga yozish + admin tasdiq
    if "telefon" not in user_data[uid]:
        telefon = text
        dacha = user_data[uid]["dacha"]
        sana = user_data[uid]["sana"]
        ism = message.from_user.full_name

        # sheetga yozamiz
        row_index = append_booking(sana, dacha, ism, telefon, uid)

        # admin tugmalar
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="ok"),
                InlineKeyboardButton(text="❌ Bekor", callback_data="no"),
            ]
        ])

        admin_msg = await bot.send_message(
            ADMIN_ID,
            f"📢 Yangi bron\n\n"
            f"🏡 {dacha}\n"
            f"📅 {sana}\n"
            f"👤 {ism}\n"
            f"📞 {telefon}\n"
            f"🧾 Holat: kutilyapti",
            reply_markup=ikb
        )

        set_admin_msg_id(row_index, admin_msg.message_id)

        await message.answer("✅ Bron yuborildi! Admin tasdiqlasa sizga xabar boradi.")
        user_data.pop(uid, None)
        return


# ===================== Admin callback ✅/❌ =====================
@dp.callback_query()
async def admin_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return

    action = call.data  # ok / no
    admin_msg_id = call.message.message_id

    row_index, row = find_row_by_admin_msg_id(admin_msg_id)
    if not row_index:
        await call.answer("Topilmadi (AdminMsgId yo‘q)", show_alert=True)
        return

    user_id = int(row.get("UserId"))
    dacha = row.get("Dacha")
    sana = row.get("Sana")

    if action == "ok":
        update_status(row_index, "tasdiqlandi")
        await bot.send_message(user_id, f"✅ Bron TASDIQLANDI!\n🏡 {dacha}\n📅 {sana}")
        await call.message.edit_text(call.message.text.replace("🧾 Holat: kutilyapti", "🧾 Holat: tasdiqlandi"))
        await call.answer("Tasdiqlandi ✅")
        return

    if action == "no":
        update_status(row_index, "bekor")
        await bot.send_message(user_id, f"❌ Bron BEKOR qilindi.\n🏡 {dacha}\n📅 {sana}")
        await call.message.edit_text(call.message.text.replace("🧾 Holat: kutilyapti", "🧾 Holat: bekor"))
        await call.answer("Bekor qilindi ❌")
        return

    await call.answer("Noma’lum buyruq", show_alert=True)


# ===================== RUN =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
