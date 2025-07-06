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

# Kanal username (link uchun ishlatiladi)
CHANNEL_USERNAME = '@AlTarjimonUz_Bot'
CHANNEL_LINK = 'https://t.me/AlTarjimonUz_Bot'

# Kino bazasi
DATA_FILE = 'data.json'
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Obuna tekshiruv
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in [ChatMember.LEFT, ChatMember.KICKED]
    except:
        return False

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            "❌ Kechirasiz, kinoni ko‘rishdan oldin quyidagi kanallarga obuna bo‘ling:\n"
            f"[➕]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return
    await update.message.reply_text(
        f"Assalomu alaykum, {user.full_name}!\nKinoning kodini kiriting:"
    )

# /add BZ01 | Kino nomi | Janr
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            "❌ Kechirasiz, kinoni qo‘shishdan oldin kanalga obuna bo‘ling:\n"
            f"[➕]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return

    text = update.message.text[len('/add '):].strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 3:
        await update.message.reply_text("❗ Format xato!\nTo‘g‘ri format:\n/add BZ01 | Kino nomi | Janr")
        return

    code, name, genre = parts
    code = code.upper()
    db[code] = {
        "name": name,
        "genre": genre,
        "views": 0
    }
    save_db()
    await update.message.reply_text(f"✅ Qo‘shildi:\n🔑 {code}\n🎬 {name}\n🎭 {genre}")

# Kodni qabul qilish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            "❌ Kechirasiz, kinoni ko‘rishdan oldin quyidagi kanallarga obuna bo‘ling:\n"
            f"[➕]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return

    code = update.message.text.strip().upper()
    if code in db:
        db[code]["views"] += 1
        save_db()
        film = db[code]
        await update.message.reply_text(
            f"🎬 Kino: {film['name']}\n"
            f"🎭 Janr: {film['genre']}\n"
            f"👁 Ko‘rilgan: {film['views']} marta"
        )
    else:
        await update.message.reply_text("❗ Bunday kod topilmadi.")

# Botni ishga tushirish
def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway uchun .env orqali
    if not BOT_TOKEN:
        print("⚠️ BOT_TOKEN o‘rnatilmagan.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
