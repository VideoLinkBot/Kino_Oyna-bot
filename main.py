import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# 🔹 Log yozuvlarini yoqish
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🔹 Telegram token
TOKEN = os.getenv("BOT_TOKEN")

# 🔹 Majburiy obuna kanallari (username holda @ belgisi bilan yoziladi)
REQUIRED_CHANNELS = ["@kino_oyna", "@rasmdamen"]  # ← shu yerga o‘zingizning kanallaringizni yozing

# 🔹 Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    not_subscribed = []

    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel)
        except:
            not_subscribed.append(channel)

    if not_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{ch[1:]}")] for ch in not_subscribed
        ]
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 *Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:*",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"👋 Assalomu alaykum, {user.first_name}!\n\n"
            "Botimizga xush kelibsiz!\n"
            "Iltimos, kodni yuboring 🔢"
        )

# 🔹 Callback tekshiruvi (✅ Tekshirish tugmasi)
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel)
        except:
            not_subscribed.append(channel)

    if not_subscribed:
        await query.edit_message_text(
            "❌ Siz hali barcha kanallarga obuna bo‘lmagansiz.\n\n"
            "Quyidagi kanallarga obuna bo‘ling va yana tekshiring.",
        )
    else:
        await query.edit_message_text(
            f"✅ Obuna tasdiqlandi!\n\n"
            f"Assalomu alaykum, {user.first_name}!\n"
            f"Kodni yuboring 🔢"
        )

# 🔹 Kodni qabul qilish
async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"📩 Siz yuborgan kod: `{text}`", parse_mode="Markdown")

# 🔹 Asosiy funksiya
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_code))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(CommandHandler("check_subs", check_subscription))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.TEXT, get_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.TEXT, get_code))

    app.add_handler(MessageHandler(filters.ALL, start))

    # Callback handler
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subs"))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
