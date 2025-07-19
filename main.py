import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalamu alaykum! Bizning botga xush kelibsiz.\nKino kodini yuboring:")

# Kino kodini tekshirish va yuborish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if user_input in data:
        file_id = data[user_input]
        await update.message.reply_video(video=file_id)
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi. Iltimos, tekshirib qayta yuboring.")

# Asosiy bot ishga tushirish
async def main():
    from os import getenv
    from dotenv import load_dotenv
    load_dotenv()
    
    TOKEN = getenv("BOT_TOKEN")  # Railway werables da BOT_TOKEN deb qo'yilgan bo'lishi kerak

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishlayapti...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
