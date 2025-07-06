import os
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATA_FILE = 'data.json'

# Ma'lumotlar bazasi
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DATA_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# /start komandasi
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎬 Xush kelibsiz!\nKod yuboring yoki admin bo‘lsangiz: /add BZ01 | Kino nomi | Janr | link")

# /add komandasi (faqat siz uchun)
def add(update: Update, context: CallbackContext):
    text = update.message.text[len('/add '):].strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 4:
        update.message.reply_text("❌ Format xato!\nTo‘g‘ri format: /add BZ01 | Kino nomi | Janr | link")
        return
    code, name, genre, link = parts
    db[code.upper()] = {"name": name, "genre": genre, "link": link}
    save_db()
    update.message.reply_text(f"✅ Qo‘shildi: {code.upper()} → {name}")

# Foydalanuvchi kod yuborsa
def handle_message(update: Update, context: CallbackContext):
    code = update.message.text.strip().upper()
    if code in db:
        k = db[code]
        update.message.reply_text(
            f"🎬 Kino: {k['name']}\n🎭 Janr: {k['genre']}\n🔗 Link: {k['link']}"
        )
    else:
        update.message.reply_text("😕 Bunday kod topilmadi.")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
