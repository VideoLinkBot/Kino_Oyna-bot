import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Admin Telegram ID (sizning ID)
ADMIN_ID = 6905227976

# Kino bazasi (json yoki dict, hozircha oddiy dict)
kino_baza = {
    "101": "https://t.me/yourchannel/123",  # misol uchun
    "102": "https://t.me/yourchannel/124",
}

logging.basicConfig(level=logging.INFO)

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data='add_movie')],
            [InlineKeyboardButton("📊 Statistika", callback_data='stats')],
            [InlineKeyboardButton("📢 Kanal", url="https://t.me/yourchannel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Admin panelga xush kelibsiz:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🎬 Kodni yuboring (masalan: 101):")

# Callback tugmalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != ADMIN_ID:
        await query.edit_message_text("Sizda ruxsat yo‘q.")
        return

    if query.data == "add_movie":
        await query.edit_message_text("Yangi kino qo‘shish uchun: `kod|link` yuboring.\n\nMasalan:\n`103|https://t.me/yourchannel/125`")
        context.user_data["adding_movie"] = True

    elif query.data == "stats":
        count = len(kino_baza)
        await query.edit_message_text(f"📊 Bazadagi kinolar soni: {count} ta")

# Kino kodi orqali kino chiqarish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id == ADMIN_ID and context.user_data.get("adding_movie"):
        try:
            code, link = text.split("|")
            kino_baza[code.strip()] = link.strip()
            await update.message.reply_text(f"✅ {code} kodi uchun kino qo‘shildi.")
        except:
            await update.message.reply_text("❌ Noto‘g‘ri format. `kod|link` ko‘rinishida yuboring.")
        context.user_data["adding_movie"] = False
        return

    # Oddiy foydalanuvchi uchun kod orqali kino
    if text in kino_baza:
        await update.message.reply_text(f"🎬 Mana siz izlagan kino:\n{kino_baza[text]}")
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi. Tekshirib qayta urinib ko‘ring.")

# Main
if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(telegram.ext.CallbackQueryHandler(button_handler))

    print("Bot ishga tushdi...")
    app.run_polling()
