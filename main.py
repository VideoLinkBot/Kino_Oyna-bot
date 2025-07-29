from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 🔐 BOT TOKEN — BU YERGA O'ZINGIZNING TOKENINGIZNI YOZING!
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 🔗 Majburiy kanal username
CHANNEL_USERNAME = "@YourChannelUsername"

# 👮‍♂️ Admin user ID ro'yxati
ADMINS = [123456789, 987654321]  # ← o'zingizni telegram ID larini yozing

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Foydalanuvchi kanalga obuna bo‘lganmi?
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status not in ("member", "administrator", "creator"):
            raise Exception("Not subscribed")
    except:
        keyboard = [
            [InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ]
        await update.message.reply_text(
            "👋 Iltimos, botdan foydalanish uchun kanalga obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Obunasi bor – adminmi yoki oddiy foydalanuvchimi tekshiramiz
    if user_id in ADMINS:
        keyboard = [
            [InlineKeyboardButton("🎬 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📢 Kanal qo‘shish", callback_data="add_channel")]
        ]
        await update.message.reply_text(
            "👮 Admin paneliga xush kelibsiz:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "🎬 Assalomu alaykum! Iltimos kino kodini kiriting."
        )

# Inline tugmalarni boshqarish
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_sub":
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await query.edit_message_text("✅ Obuna tasdiqlandi. Endi botdan foydalanishingiz mumkin.")
        else:
            await query.edit_message_text("❌ Siz hali ham kanalga obuna bo‘lmadingiz.")
    elif query.data == "add_movie" and user_id in ADMINS:
        await query.edit_message_text("🎬 Kino qo‘shish funksiyasi ishlamoqda (hali to‘liq emas).")
    elif query.data == "add_channel" and user_id in ADMINS:
        await query.edit_message_text("📢 Kanal qo‘shish funksiyasi ishlamoqda (hali to‘liq emas).")
    else:
        await query.edit_message_text("⛔ Sizda bu amalga ruxsat yo‘q.")

# Kino kodi yoki admin xabarlari
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in ADMINS:
        await update.message.reply_text(f"🔍 Siz yuborgan kod: {text}\n(Kino qidirilmoqda...)")
    else:
        await update.message.reply_text(f"✅ Admin xabari qabul qilindi: {text}")

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
