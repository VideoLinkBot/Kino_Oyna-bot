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

ADMIN_ID = 6905227976
REQUIRED_CHANNEL = "@YOURCHANNEL"  # <-- Shu yerga kanal username'ni yozing, masalan: @kinolaruz
KINOLAR_FILE = "kinolar.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def load_movies():
    if os.path.exists(KINOLAR_FILE):
        with open(KINOLAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_movies(data):
    with open(KINOLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Admin panelga xush kelibsiz:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🎬 Kino kodini yuboring (masalan, 101):")

# Tugma bosilganda ishlaydigan funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

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

# Kino kodi yoki admin qo‘shishi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    movies = load_movies()

    # ADMIN kino qo‘shyapti
    if user_id == ADMIN_ID and context.user_data.get("adding_movie"):
        try:
            code, link = text.split("|")
            code = code.strip()
            link = link.strip()
            movies[code] = link
            save_movies(movies)
            await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo‘shildi: {code}")
        except Exception:
            await update.message.reply_text("❌ Format noto‘g‘ri. Iltimos, `kod|link` formatida yuboring.")
        context.user_data["adding_movie"] = False
        return

    # ODDIY FOYDALANUVCHI KANALGA A’ZOmi?
    if user_id != ADMIN_ID:
        try:
            member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
            if member.status in ("left", "kicked"):
                raise Exception("Not a member")
        except:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]])
            await update.message.reply_text("Iltimos, kanalga obuna bo‘ling:", reply_markup=btn)
            return

    # Kino kodi bilan qidiruv
    if text in movies:
        await update.message.reply_text(f"🎬 Kino topildi:\n{movies[text]}")
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi. To‘g‘ri kiriting.")

# Dastur ishga tushishi
if __name__ == "__main__":
    from dotenv import load_dotenv

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
