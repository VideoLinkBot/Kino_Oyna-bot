import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"  # Sizning bot tokeningiz shu yerda

def load_db():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "Foydalanuvchi"
    await update.message.reply_text(
        f"Assalomu alaykum, {name}!\n"
        "Kinoning kodini kiriting.\n"
        "Masalan: BZ01"
    )

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    code = update.message.text.strip().upper()

    if code in db:
        film = db[code]
        film["views"] += 1
        save_db(db)
        await update.message.reply_text(
            f"Kino: {film['name']}\n"
            f"Janr: {film['genre']}\n"
            f"Ko‘rilgan: {film['views']} marta"
        )
        await update.message.reply_video(film["file_id"])
    else:
        await update.message.reply_text("Bunday kod topilmadi!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.run_polling()
