import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
from datetime import datetime, timedelta

# ====== CONFIG ======
BOT_TOKEN = os.getenv("8537176060:AAHaAaTR3AJ3PAyL2080MhRCIMIjBF_UG3w")          # Telegram Bot token
ADMIN_ID = int(os.getenv("5523459970"))       # Sizning Telegram ID
GOOGLE_SHEET_ID = os.getenv("1ewal_UpZ4M64Nk6Pa_L46Zwm0HYt--AUKRueBcY2H_Y")  # Google Sheet ID
GOOGLE_CREDENTIALS = os.getenv("{
  "type": "service_account",
  "project_id": "dacha-486420",
  "private_key_id": "c798753c02f0aab71c8d1d6e114081ed3e2d5e53",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCnn73Ue5j2bnJP\nD9/YdqQmFjvhweGuvmGsOSthNbTbK1PO3d/JHsS/b2q0eftbu403a6/W/AIt8i5U\nXm46ywIl3xKOKUVc++mrP9cGLRPPeU9HnUhmuKEJOYrQXuE9DZAv4DYvI/Gd4pfu\nqPhoOCm/R/OdoTKa/P4D79pyoOPPblxIzEbxz66gOxtsVV26EPaHTM4tVOa8kVtW\nK6cbEMI7uHNhSodtj84K6hYEdBIf1FBDK3nCroklTMtFOE7MJ2Q5BpTCYyIHQzBV\nlswGTN7OBtNVp+NQ9ImEHSxz1UTedXjSkF2joO7hCsK4yGL6ajDSSzIisIYYzG09\nZHz/VYVxAgMBAAECggEADnmtf3ly8qkEBw7UYlGQiFd4MV04W4pGTgSb2ee06A5c\nTOt9JVWaYPvCp7Y2/it6nPQYOcUGfShCVvfWpg4c799NL2ih/E8m1SqMq5Rd9xc/\nQOx0saY1BeJpuefPpKGUt4WxuC1u8pb8TthZp0peVI3mnFCs2ZSKbRWb9DUvpxx5\nRAnlPCjy+J+tnI496CUzrcGf3V7f3lekoJfDbkfWmwEKzwV5ICbBkJ2TH1ezT9zB\n8sciZkzid2zkqDtmXLkrY0GqxOSZKvuSOsAciU5gNLhZRcprZxqn3ZYBs6sRP0Gf\nBYkR924u7+v6PRnyiShKp6/y5W6LWXO8cCMB0mvdHwKBgQDho373Jev16q5W35rQ\nzEHml8VqhF0tKAp4LH4cyp/JIEw4rp2GpuGDUkXz9FbWFtbPeyY5flvRtwS1hUTs\n7xIT1xL1h2vDUC1K6zES9Shmy41zjtivPo8mipVOakxdt0kkxlCvy/eqEb2vmNze\nYFHwfrb+Ps2HyJ4UP2fT/TfDFwKBgQC+LdUi1OfDladDmb1yeOuLeIFeJElWmV3L\nPwKxDgx4EARnYs2Qi7OTDkMeYVEQuJWQiy1u4hXXsOT/MfWpjaySBSExmpLbpZ1Q\n8bLPjUSELFXds2sGUSHsBZdelVzNzrmDPfqhOOJcE+bcqObaStpnF7rlddvEEzPC\nDZhVcTlwtwKBgGDiPuYIFmUlO2553JPC4JkOmem+o/N7ueMX156tMia+A3xjHahv\nh21HqlmxlIegjuPP0P3mz64gk5kNfCbwECcMtktOtmrKxmfgzNWDBrH8vOPddhTp\nG7ZE0w80fU3QIUv1CzgwsEsKCxSW4l9ppEVLY2+Pr9iZv6aaAw73LzZJAoGARgoL\nHLDcSiOrXjIYmzf9R3gx7MHgYIxLBrdF/n72CKGdfZXdrwZENDxka6PbfxT7wCgB\nq3yIHs9/Bp0XpEIQ9BX/i40p2Mq9jTn2aInWWfcaCHQzTjhDDfFhNew8KW+g0rzY\nuNeCRfbuZwWtP2eh16XdpvQo46VOwoDPQWhZhzECgYEAhxvmnxmUd9y6EgHpiLto\nrS/G4jFGgy0G3Iyvvn7lMlgo0wwtbS3ePADyNbZP9Cb/hyZqEAUHeSru2RpttUFz\nR8y22BZA3HFkGW0/iS4txvmNIe4C4bKNVwxQ3bO3yAJLiF51WxoOugBn/G5jauus\neykpboQUyRTifgswSQI4lnQ=\n-----END PRIVATE KEY-----\n",
  "client_email": "oiladacha@dacha-486420.iam.gserviceaccount.com",
  "client_id": "111162537360709109580",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/oiladacha%40dacha-486420.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
")  # JSON matni

# ====== Google Sheets Setup ======
cred_dict = json.loads(GOOGLE_CREDENTIALS)
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1

# ====== Telegram Bot Setup ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

# ====== Helper: Bo'sh sanalarni olish ======
def get_available_dates(dacha):
    all_rows = sheet.get_all_records()
    taken_dates = [row["Sana"] for row in all_rows if row["Dacha"] == dacha]
    available = []
    for i in range(30):  # keyingi 30 kun
        day = datetime.today() + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        if day_str not in taken_dates:
            available.append(day_str)
    return available

# ====== /start Command ======
@dp.message(Command("start"))
async def start(message: types.Message):
    dacha_list = list(dict.fromkeys(sheet.col_values(2)[1:]))  # B2 va past
    buttons = []
    for i in range(0, len(dacha_list), 2):
        row = [KeyboardButton(dacha_list[i])]
        if i+1 < len(dacha_list):
            row.append(KeyboardButton(dacha_list[i+1]))
        buttons.append(row)
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Assalomu alaykum! Dachani tanlang:", reply_markup=kb)

# ====== Booking Flow ======
@dp.message()
async def booking(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # 1️⃣ Dacha tanlash
    if user_id not in user_data:
        user_data[user_id] = {"dacha": text}
        available_dates = get_available_dates(text)
        buttons = [[KeyboardButton(d)] for d in available_dates[:10]]  # faqat 10 ta
        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Iltimos, bron qilish sanasini tanlang:", reply_markup=kb)
        return

    # 2️⃣ Sana tanlash
    if "sana" not in user_data[user_id]:
        user_data[user_id]["sana"] = text
        await message.answer("Iltimos, telefon raqamingizni kiriting:")
        return

    # 3️⃣ Telefon kiritish
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

        # Foydalanuvchiga xabar
        await message.answer(f"Rahmat! Siz {dacha}ni {sana} sanaga bron qildingiz ✅")

        # User state tozalash
        user_data.pop(user_id)
        return

# ====== Run Bot ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

