import os
import requests
import pandas as pd
from flask import Flask
from threading import Thread
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from io import BytesIO
from PIL import ImageFont

# Load Hadith Data
hadith_data = pd.read_excel("hadith.xlsx")

# Load Quran font
FONT_PATH = "quran.ttf"
try:
    font = ImageFont.truetype(FONT_PATH, 24)
except IOError:
    font = ImageFont.load_default()

# Telegram Bot Token
TELEGRAM_API_TOKEN = '7476023842:AAFyYp9fkQ5zXyJ7DXvXfj0TSg974q5q6O0'

# Flask Keep Alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# Get Surahs from API
def get_surahs():
    url = "https://api.alquran.cloud/v1/surah"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [{'id': s['number'], 'name': s['name'], 'ayah_count': s['numberOfAyahs']} for s in data['data']]
    return []

# Surah Keyboard
def get_surah_keyboard(page=1, per_page=50):
    surahs = get_surahs()
    start, end = (page - 1) * per_page, min(page * per_page, len(surahs))
    keyboard = [[InlineKeyboardButton(f"{s['id']}: {s['name']}", callback_data=f"surah-{s['id']}")] for s in surahs[start:end]]
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page-{page - 1}"))
    if end < len(surahs):
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page-{page + 1}"))
    if nav:
        keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

# Ayah Keyboard
def get_ayah_keyboard(surah, total, page=1, per_page=50):
    start, end = (page - 1) * per_page + 1, min(page * per_page, total)
    keyboard = [[InlineKeyboardButton(f"Ayah {i}", callback_data=f"ayah-{surah}-{i}")] for i in range(start, end + 1)]
    nav = []
    if start > 1:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"ayahpage-{surah}-{page - 1}"))
    if end < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"ayahpage-{surah}-{page + 1}"))
    if nav:
        keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

# Main Menu
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Quran", callback_data="menu-quran"),
         InlineKeyboardButton("🕌 Hadith", callback_data="menu-hadith")]
    ])

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=get_main_menu())

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome back! Choose an option:", reply_markup=get_main_menu())

async def quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("You selected Quran! Choose a Surah:", reply_markup=get_surah_keyboard())

async def hadith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"Hadith {i}", callback_data=f"hadith-{i}")] for i in hadith_data['id']]
    await update.message.reply_text("You selected Hadith! Choose a Hadith:", reply_markup=InlineKeyboardMarkup(keyboard))

# Menu Handler
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu-quran":
        await query.edit_message_text("Select a Surah:", reply_markup=get_surah_keyboard())
    elif query.data == "menu-hadith":
        keyboard = [[InlineKeyboardButton(f"Hadith {i}", callback_data=f"hadith-{i}")] for i in hadith_data['id']]
        await query.edit_message_text("Select a Hadith:", reply_markup=InlineKeyboardMarkup(keyboard))

# Hadith Details
async def handle_hadith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    h_id = int(query.data.split('-')[1])
    h = hadith_data[hadith_data['id'] == h_id].iloc[0]
    message = f"📜 *Hadith {h['id']}*\n\n*Arabic:*\n{h['hadith_ar']}\n\n*Kurdish:*\n{h['hadith_ku']}\n\n*Sahih:* {h['hadith_sahih']}\n*Explanation:* {h['hadith_geranawa']}"
    await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# Surah Pagination
async def handle_surah_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('-')[1])
    await query.edit_message_text("Select a Surah:", reply_markup=get_surah_keyboard(page))

# Surah Selection
async def handle_select_surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    surah_id = int(query.data.split('-')[1])
    context.user_data['surah'] = surah_id
    surahs = get_surahs()
    surah = next(s for s in surahs if s['id'] == surah_id)
    await query.message.reply_text(f"Surah {surah['name']} selected. Now select an Ayah:", reply_markup=get_ayah_keyboard(surah_id, surah['ayah_count']))

# Ayah Page Handler
async def handle_ayah_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, surah, page = query.data.split('-')
    surah = int(surah)
    page = int(page)
    surahs = get_surahs()
    selected = next(s for s in surahs if s['id'] == surah)
    await query.message.edit_text(f"Surah {selected['name']} selected. Now select an Ayah:", reply_markup=get_ayah_keyboard(surah, selected['ayah_count'], page))

# Fetch Ayah Handler
async def fetch_ayah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # IMPORTANT: answer first to avoid timeout

    _, surah, ayah = query.data.split('-')
    surah, ayah = int(surah), int(ayah)

    try:
        # Arabic
        arabic_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
        arabic_response = requests.get(arabic_url)
        arabic_response.raise_for_status()
        arabic_text = arabic_response.json()['data']['text']

        # Kurdish (Asan)
        kurdish_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ku.asan"
        kurdish_response = requests.get(kurdish_url)
        kurdish_response.raise_for_status()
        kurdish_text = kurdish_response.json()['data']['text']

        # Reply text
        message = f"📖 *Surah {surah}, Ayah {ayah}*\n\n*Arabic:*\n{arabic_text}\n\n*Kurdish:*\n{kurdish_text}"
        await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

        # Audio
        surah_str = str(surah).zfill(3)
        ayah_str = str(ayah).zfill(3)
        audio_url = f"https://everyayah.com/data/Yasser_Ad-Dussary_128kbps/{surah_str}{ayah_str}.mp3"
        await query.message.reply_voice(audio_url, caption=f"🎧 Surah {surah}, Ayah {ayah}")

    except Exception as e:
        print("Error:", e)
        await query.message.reply_text("❌ Failed to fetch Ayah.")

# Run the Bot
if __name__ == '__main__':
    app_telegram = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Commands
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("home", home))
    app_telegram.add_handler(CommandHandler("quran", quran))
    app_telegram.add_handler(CommandHandler("hadith", hadith))

    # Callback Query Handlers
    app_telegram.add_handler(CallbackQueryHandler(handle_menu, pattern=r"^menu-.*$"))
    app_telegram.add_handler(CallbackQueryHandler(handle_hadith, pattern=r"^hadith-\d+$"))
    app_telegram.add_handler(CallbackQueryHandler(handle_surah_page, pattern=r"^page-\d+$"))
    app_telegram.add_handler(CallbackQueryHandler(handle_select_surah, pattern=r"^surah-\d+$"))
    app_telegram.add_handler(CallbackQueryHandler(handle_ayah_page, pattern=r"^ayahpage-\d+-\d+$"))
    app_telegram.add_handler(CallbackQueryHandler(fetch_ayah, pattern=r"^ayah-\d+-\d+$"))

    print("✅ Bot is running...")
    app_telegram.run_polling()
