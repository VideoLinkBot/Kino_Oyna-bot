import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

# Tokenni shu yerga yozing
TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"

# Kino fayli
DATA_FILE = "data.json"

# Statistika
stats = {
    "kino_soni": 0,
    "qidiruvlar": 0,
}


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_movie(code, title, url):
    data = load_data()
    data.append({"code": code, "title": title, "url": url})
    save_data(data)
    stats["kino_soni"] += 1


def find_movie_by_code(code):
    stats["qidiruvlar"] += 1
    data = load_data()
    for movie in data:
        if movie["code"] == code:
            return movie
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎬 Kino qidirish", callback_data="search")],
        [InlineKeyboardButton("➕ Kino qo'shish", callback_data="add")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Assalomu alaykum!\nQanday yordam bera olaman?", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        context.user_data["action"] = "search"
        await query.message.reply_text("🔍 Kino kodini kiriting:")

    elif query.data == "add":
        context.user_data["action"] = "add_code"
        await query.message.reply_text("🎬 Kino kodi kiriting:")

    elif query.data == "stats":
        msg = f"📊 Statistika:\n\n➕ Qo‘shilgan kinolar: {stats['kino_soni']}\n🔍 Qidiruvlar soni: {stats['qidiruvlar']}"
        await query.message.reply_text(msg)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    action = context.user_data.get("action")

    if action == "search":
        movie = find_movie_by_code(text)
        if movie:
            msg = f"🎬 Kino topildi:\n\nNomi: {movie['title']}\n📥 Havola: {movie['url']}"
        else:
            msg = "❌ Bu kodga mos kino topilmadi."
        await update.message.reply_text(msg)

    elif action == "add_code":
        context.user_data["new_code"] = text
        context.user_data["action"] = "add_title"
        await update.message.reply_text("🎬 Kino nomini kiriting:")

    elif action == "add_title":
        context.user_data["new_title"] = text
        context.user_data["action"] = "add_url"
        await update.message.reply_text("📥 Kino havolasini kiriting:")

    elif action == "add_url":
        code = context.user_data.get("new_code")
        title = context.user_data.get("new_title")
        url = text
        add_movie(code, title, url)
        await update.message.reply_text("✅ Kino qo‘shildi!")
        context.user_data.clear()

    else:
        await update.message.reply_text("Iltimos, quyidagi tugmalardan birini tanlang /start orqali.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot ishga tushdi...")
    app.run_polling()
