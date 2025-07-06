import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 BOT TOKENNI BU YERGA QO'YING
BOT_TOKEN = "YOUR_BOT_TOKEN"  8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY

# 📁 data.json fayldan kino ma'lumotlarini o'qish
def load_db():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 📁 Faylga saqlash funksiyasi
def save_db(db):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

# ▶ /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "foydalanuvchi"
    
    # 🎉 Salomlashish xabari
    await update.message.reply_text(
        f"👋 Assalom Aleykum, {name}!\n"
        "🎬 Xush kelibsiz! Kodni kiriting va kinoni ko‘ring.\n"
        "🎟 Masalan: BZ01"
    )

# 🎞 Kod kirganda kinoni chiqarish
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    code = update.message.text.strip().upper()

    if code in db:
        film = db[code]
        film["views"] += 1
        save_db(db)

        # Avval ma'lumot
        await update.message.reply_text(
            f"🎬 Kino: {film['name']}\n"
            f"🎭 Janr: {film['genre']}\n"
            f"👁 Ko‘rilgan: {film['views']} marta"
        )
        # Keyin video
        await update.message.reply_video(film["file_id"])
    else:
        await update.message.reply_text("❗ Bunday kod topilmadi.")

# 🚀 Botni ishga tushurish
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
