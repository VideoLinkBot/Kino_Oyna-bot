import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Kino bazasi
with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "Foydalanuvchi"
    await update.message.reply_text(
        f"👋 Assalomu alaykum {name} botimizga xush kelibsiz.\n\n✍️ Kino kodini yuboring."
    )

# Kodni qayta ishlash
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text in data:
        kino = data[text]
        await update.message.reply_video(
            video=kino["file_id"],
            caption=f"🎬 Kino\n📛 {kino['title']}\n📺 {kino['part']} - qism"
        )
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi. Kodni tekshirib yuboring.")

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    print("🤖 Bot ishga tushdi...")
    app.run_polling()
