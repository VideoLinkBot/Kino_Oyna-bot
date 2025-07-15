import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Railway'dan token olish
TOKEN = os.getenv("BOT_TOKEN")

# Kodga mos kinolar (bazani xohlasang keyinchalik json faylga chiqarib ajratib beraman)
kino_data = {
    "1": {
        "title": "Spider-Man: No Way Home",
        "file_id": "AAMCBAADGQECG-nFaHaHPJqGgs0wgSDY9cGlgc6BW0kAAv4KAALA7jFRLlxzqg1wXnMBAAdtAAM2BA"
    },
    "2": {
        "title": "Avengers: Endgame (Tarjima)",
        "file_id": "AAMCBQADGQECh-gAaHa1234567890exampleexample"
    }
}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Salom! Menga kino kodini yozing, men sizga kinoni yuboraman.")

# Kod yuborilganida ishlovchi funksiya
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    kino = kino_data.get(code)

    if kino:
        await update.message.reply_video(
            video=kino["file_id"],
            caption=f"🎥 {kino['title']}\nKod: {code}"
        )
    else:
        await update.message.reply_text("❌ Kechirasiz, bu kodga mos kino topilmadi.")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

app.run_polling()
