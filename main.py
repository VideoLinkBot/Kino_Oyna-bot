import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Majburiy obuna kanali
REQUIRED_CHANNEL = "@SizningKanalUsername"

# Foydalanuvchining kanalga obuna bo‘lganligini tekshirish
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    is_subscribed = await check_subscription(user.id, context)

    if not is_subscribed:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
            [InlineKeyboardButton("🔄 Tekshirish", callback_data="check_subs")]
        ])
        await update.message.reply_text(
            "👋 Botdan foydalanish uchun kanalga obuna bo‘ling:",
            reply_markup=keyboard
        )
        return

    await update.message.reply_text("🎬 Iltimos, kino kodini kiriting:")

# Callback tugma tekshiruvi
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        await query.edit_message_text("✅ Obuna tasdiqlandi! Endi kino kodini kiriting.")
    else:
        await query.edit_message_text("❗ Siz hali kanalga obuna bo‘lmadingiz.")

# Kino kodi asosida kino chiqarish
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_subscribed = await check_subscription(user_id, context)

    if not is_subscribed:
        await update.message.reply_text("❗ Avval kanalga obuna bo‘ling.")
        return

    code = update.message.text.strip()

    try:
        with open("data.json", "r") as f:
            data = json.load(f)

        if code in data:
            kino = data[code]
            await update.message.reply_text(
                f"🎬 <b>{kino['title']}</b>\n"
                f"📝 {kino['description']}\n"
                f"▶️ <a href='{kino['link']}'>Kinoni ko‘rish</a>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ Bunday kod mavjud emas.")
    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi.")

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token("BOT_TOKENINGIZNI_BU_YERGA_QO‘YING").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, start))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.ALL, handle_code))

    app.run_polling()

if __name__ == '__main__':
    main()
