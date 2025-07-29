import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

kino_data = {
    "100": "https://t.me/kanalingiz/1",
    "101": "https://t.me/kanalingiz/2"
}

user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Obuna tekshiruvi
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status not in ("member", "creator", "administrator"):
            raise Exception("Not subscribed")
    except:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Obuna bo'lish", url=f"https://t.me/{str(CHANNEL_ID).replace('-100','')}")]])
        await update.message.reply_text("❗ Botdan foydalanish uchun kanalga obuna bo‘ling.", reply_markup=btn)
        return

    user_stats[user_id] = datetime.now().date()
    if str(user_id) == str(ADMIN_ID):
        btn = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("🗑 Kanallarni bekor qilish", callback_data="reset_channels")]
        ]
        await update.message.reply_text("🎛 Admin paneliga xush kelibsiz!", reply_markup=InlineKeyboardMarkup(btn))
    else:
        username = update.effective_user.username or "Foydalanuvchi"
        await update.message.reply_text(f"Assalomu alaykum @{username}, botimizga xush kelibsiz!\n\n🎬 Kino kodini yuboring:")

# Kino kodini tekshirish
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Obuna tekshiruvi
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status not in ("member", "creator", "administrator"):
            raise Exception("Not subscribed")
    except:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Obuna bo'lish", url=f"https://t.me/{str(CHANNEL_ID).replace('-100','')}")]])
        await update.message.reply_text("❗ Botdan foydalanish uchun kanalga obuna bo‘ling.", reply_markup=btn)
        return

    code = update.message.text.strip()
    if code in kino_data:
        await update.message.reply_text(f"✅ Mana kinongiz: {kino_data[code]}")
    else:
        await update.message.reply_text("🚫 Bunday kodga mos kino topilmadi.")

# Admin tugmalari
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if str(user_id) != str(ADMIN_ID):
        await query.edit_message_text("🚫 Siz admin emassiz.")
        return

    if query.data == "add_movie":
        await query.edit_message_text("🎥 Kino qo‘shish uchun quyidagi formatda yozing:\n\n<code>kod=https://link</code>")
    elif query.data == "stats":
        kunlik = sum(1 for v in user_stats.values() if v == datetime.now().date())
        await query.edit_message_text(f"📊 Bugun {kunlik} ta foydalanuvchi kirgan.")
    elif query.data == "reset_channels":
        await query.edit_message_text("❌ Kanal o‘zgartirish uchun `.env` faylidan CHANNEL_ID ni yangilang.")

# Admin kino qo‘shadi
async def add_kino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) != str(ADMIN_ID):
        return

    if "=" in update.message.text:
        code, link = update.message.text.split("=", 1)
        kino_data[code.strip()] = link.strip()
        await update.message.reply_text(f"✅ {code.strip()} kodi uchun kino qo‘shildi.")
    else:
        await update.message.reply_text("❗ Noto‘g‘ri format. Foydalaning: <code>kod=https://link</code>")

# Asosiy bot ishlovchisi
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_callback))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(int(ADMIN_ID)) & ~filters.COMMAND, add_kino))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
