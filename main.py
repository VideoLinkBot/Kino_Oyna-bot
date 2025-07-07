import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"  # ← Sizning bot tokeningiz

# Kino fayllarini yuklash
def load_db():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum! Botga xush kelibsiz!\n\n"
        "🎬 Kino ko‘rish uchun kodni yozing.\n"
        "Kod bo‘yicha sizga kinoni yuboraman ✅"
    )

# Kodni qayta ishlash
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    code = update.message.text.strip()

    if code.isdigit():
        if code in db:
            file_id = db[code]["file_id"]
            await update.message.reply_text("📽 Kinoni yuboraman ✅")
            await update.message.reply_video(file_id)
        else:
            await update.message.reply_text("❗ Bunday kod topilmadi.")
    else:
        await update.message.reply_text("❗ Faqat raqam yozing. Masalan: 15")

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_code))
app.run_polling()
