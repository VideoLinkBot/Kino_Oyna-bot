import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest
from dotenv import load_dotenv

# === CONFIGURATION ===

# Admin Telegram ID
ADMIN_ID = 6905227976

# Kino ma'lumotlarini saqlash fayli
KINOLAR_FILE = "kinolar.json"

# Majburiy obuna talab qilinadigan kanallar
REQUIRED_CHANNELS = [
    {"username": "@yourchannel1", "name": "Kanal 1"},
    {"username": "@yourchannel2", "name": "Kanal 2"},
]

# === LOGGING ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === FUNCTIONS ===

def load_movies():
    if os.path.exists(KINOLAR_FILE):
        with open(KINOLAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_movies(data):
    with open(KINOLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# === HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("📢 Kanal", url="https://t.me/YOURCHANNEL")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Admin panelga xush kelibsiz:", reply_markup=reply_markup
        )
        return

    # === Majburiy obuna tekshiruvi ===
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "creator", "administrator"]:
                not_subscribed.append(channel)
        except BadRequest:
            not_subscribed.append(channel)

    if not_subscribed:
        buttons = [
            [InlineKeyboardButton(f"✅ {ch['name']}", url=f"https://t.me/{ch['username'].lstrip('@')}")]
            for ch in not_subscribed
        ]
        buttons.append([InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_subscription")])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text("🎬 Kino kodini yuboring (masalan, 101):")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_subscription":
        not_subscribed = []
        for channel in REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
                if member.status not in ["member", "creator", "administrator"]:
                    not_subscribed.append(channel)
            except BadRequest:
                not_subscribed.append(channel)

        if not_subscribed:
            await query.edit_message_text("❌ Hali ham barcha kanallarga obuna bo‘lmadingiz.")
        else:
            await query.edit_message_text("✅ Rahmat! Endi kino kodini yuboring.")
        return

    if user_id != ADMIN_ID:
        await query.edit_message_text("Sizda ruxsat yo‘q.")
        return

    if query.data == "add_movie":
        await query.edit_message_text(
            "Yangi kino qo‘shish uchun `kod|link` formatida yuboring.\n\nMasalan:\n101|https://t.me/yourchannel/123"
        )
        context.user_data["adding_movie"] = True

    elif query.data == "stats":
        movies = load_movies()
        count = len(movies)
        await query.edit_message_text(f"📊 Bazadagi kinolar soni: {count} ta")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    movies = load_movies()

    # Admin kino qo‘shmoqda
    if user_id == ADMIN_ID and context.user_data.get("adding_movie"):
        try:
            code, link = text.split("|")
            code = code.strip()
            link = link.strip()
            movies[code] = link
            save_movies(movies)
            await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo‘shildi: {code}")
        except Exception:
            await update.message.reply_text(
                "❌ Format noto‘g‘ri. Iltimos, `kod|link` ko‘rinishida yuboring."
            )
        context.user_data["adding_movie"] = False
        return

    # Oddiy foydalanuvchi kino kodi yuboradi
    if text in movies:
        await update.message.reply_text(f"🎬 Kino topildi:\n{movies[text]}")
    else:
        await update.message.reply_text(
            "❌ Bunday kod topilmadi. Iltimos, to‘g‘ri kod kiriting."
        )

# === MAIN ===

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: BOT_TOKEN .env faylida yo'q!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
