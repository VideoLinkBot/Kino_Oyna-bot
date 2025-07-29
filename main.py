import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

# 🔧 O'ZINGNING TOKENINGNI SHU YERGA QO'Y!
BOT_TOKEN = '8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY'
CHANNEL_ID = '@Kino_Oyna'  # Kanal usernameni @ bilan yozing

logging.basicConfig(level=logging.INFO)

async def check_user_membership(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            try:
                status = data["result"]["status"]
                return status in ["member", "creator", "administrator"]
            except:
                return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_user_membership(user_id)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Botdan foydalanish uchun kanalga obuna bo‘ling:", reply_markup=reply_markup)
    else:
        buttons = [
            [KeyboardButton("🎬 Kino qo‘shish")],
            [KeyboardButton("📊 Statistika")],
            [KeyboardButton("➕ Kanal qo‘shish")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Xush kelibsiz! Quyidagilardan birini tanlang:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check":
        user_id = query.from_user.id
        is_member = await check_user_membership(user_id)
        if is_member:
            buttons = [
                [KeyboardButton("🎬 Kino qo‘shish")],
                [KeyboardButton("📊 Statistika")],
                [KeyboardButton("➕ Kanal qo‘shish")]
            ]
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await query.message.reply_text("✅ Obuna tasdiqlandi!", reply_markup=reply_markup)
        else:
            await query.message.reply_text("❌ Hali obuna bo‘lmadingiz. Iltimos, avval kanalga obuna bo‘ling.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))  # Xatolik chiqmasligi uchun
    app.add_handler(MessageHandler(filters.COMMAND, start))  # Barcha komandalarni ushlab turadi
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, start))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, start))

    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
