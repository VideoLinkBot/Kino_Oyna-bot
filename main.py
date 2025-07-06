import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

DATA_FILE = 'data.json'

# Ma'lumotlar bazasini yuklash
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        db = json.load(f)
else:
    db = {}

# Ma'lumotlar bazasini saqlash
def save_db():
    with open(DATA_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Xush kelibsiz!\nKod yuboring yoki admin bo‘lsangiz:\n"
        "/add BZ01 | Kino nomi | Janr | https://link"
    )

# /add komandasi (yangi kino qo‘shish)
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[len('/add '):].strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 4:
        await update.message.reply_text("❌ Format xato!\nTo‘g‘ri format:\n/add BZ01 | Kino nomi | Janr | link")
        return
    code, name, genre, link = parts
    db[code.upper()] = {"name": name, "genre": genre, "link": link}
    save_db()
    await update.message.reply_text(f"✅ Qo‘shildi:\n🔑 {code.upper()}\n🎬 {name}")

# Kodni tekshirish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    if code in db:
        k = db[code]
        await update.message.reply_text(
            f"🎬 Kino: {k['name']}\n🎭 Janr: {k['genre']}\n🔗 Link: {k['link']}"
        )
    else:
        await update.message.reply_text("😕 Bunday kod topilmadi.")

# Botni ishga tushirish
def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
