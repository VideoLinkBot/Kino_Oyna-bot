import os
import json
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

CHANNEL_USERNAME = '@AlTarjimonUz_Bot'
DATA_FILE = 'data.json'

# Ma'lumotlarni yuklash
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in [ChatMember.LEFT, ChatMember.KICKED]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Assalomu alaykum, {user.full_name}!")
    if not await is_subscribed(update, context):
        await update.message.reply_text(f"Iltimos, kanalimizga obuna bo‘ling: {CHANNEL_USERNAME}")
        return
    await update.message.reply_text("Xush kelibsiz! Kinoning kodini kiriting.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(f"Iltimos, kanalimizga obuna bo‘ling: {CHANNEL_USERNAME}")
        return

    text = update.message.text[len('/add '):].strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 3:
        await update.message.reply_text(
            "❌ Format xato!\nTo‘g‘ri format:\n/add BZ01 | Kino nomi | Janr"
        )
        return

    code, name, genre = parts
    code = code.upper()
    if code in db:
        await update.message.reply_text(f"❗ Bu kod allaqachon mavjud.")
        return

    db[code] = {
        "name": name,
        "genre": genre,
        "views": 0
    }
    save_db()
    await update.message.reply_text(f"✅ Kino qo‘shildi:\n🔑 {code}\n🎬 {name}\n🎭 {genre}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(f"Iltimos, kanalimizga obuna bo‘ling: {CHANNEL_USERNAME}")
        return

    code = update.message.text.strip().upper()
    if code in db:
        db[code]['views'] += 1  # Ko‘rilganlar sonini oshiramiz
        save_db()
        k = db[code]
        await update.message.reply_text(
            f"🎬 Kino: {k['name']}\n"
            f"🎭 Janr: {k['genre']}\n"
            f"👁 Ko‘rilganlar soni: {k['views']}"
        )
    else:
        await update.message.reply_text("😕 Bunday kod topilmadi.")

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushmoqda...")
    app.run_polling()

if __name__ == '__main__':
    main()
