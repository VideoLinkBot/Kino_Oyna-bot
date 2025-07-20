import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# .env fayldan token va admin_id o'qish
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Log sozlamasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tugmalar menyusi
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📢 Kanallar sozlamalari", callback_data="kanal")],
        [InlineKeyboardButton("📺 Kino sozlamalari", callback_data="kino")],
        [InlineKeyboardButton("🧑‍💼 Adminlar sozlamalari", callback_data="adminlar")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stat")],
        [InlineKeyboardButton("✉️ Xabar Yuborish", callback_data="xabar")],
        [InlineKeyboardButton("🤖 Bot holati", callback_data="status")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Kechirasiz, siz admin emassiz.")
        return

    await update.message.reply_text("Quyidagilardan birini tanlang:", reply_markup=get_main_menu())

# Tugmalarni ishlovchi funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    response = {
        "kanal": "📢 Kanallarni sozlash bo‘limi.",
        "kino": "📺 Kinolar bilan ishlash bo‘limi.",
        "adminlar": "🧑‍💼 Adminlar ro‘yxati.",
        "stat": "📊 Bot statistikasi.",
        "xabar": "✉️ Xabar yuborish oynasi.",
        "status": "🤖 Bot holati: aktiv.",
        "back": "⬅️ Bosh menyuga qaytdingiz."
    }

    text = response.get(data, "Noma'lum buyruq.")
    await query.edit_message_text(text, reply_markup=get_main_menu())

# Asosiy ishga tushirish
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot ishga tushdi...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
