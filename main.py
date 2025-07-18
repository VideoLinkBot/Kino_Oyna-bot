import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")  # .env fayldan tokenni oladi

# Salomlashuv komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum!\nRaqam yuboring, men sizga kinoni yuboraman.")

# Foydalanuvchi raqam yuborganida file_id ni topib, video yuborish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        raqam = text
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if raqam in data:
                file_id = data[raqam]
                await update.message.reply_video(video=file_id)
            else:
                await update.message.reply_text("Bunday raqamdagi kino topilmadi.")
        except Exception as e:
            await update.message.reply_text(f"Xatolik yuz berdi: {e}")
    else:
        await update.message.reply_text("Iltimos, faqat raqam yuboring.")

# Botni ishga tushirish
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
