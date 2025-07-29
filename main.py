import json
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_ID

    # Kanalga a'zo bo'lganini tekshirish
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "creator", "administrator"]:
            raise Exception("Not subscribed")
    except:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
        ])
        await update.message.reply_text("❗ Botdan foydalanish uchun avval kanalga obuna bo‘ling!", reply_markup=btn)
        return

    # Tugmalar
    if is_admin:
        buttons = [
            [InlineKeyboardButton("🎬 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel")]
        ]
    else:
        buttons = []

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text("🎟 Kino kodini kiriting:", reply_markup=reply_markup)

async def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    data = load_data()
    if text in data:
        await update.message.reply_text(f"🎥 {data[text]}")
    else:
        await update.message.reply_text("🚫 Bunday kodli kino topilmadi.")

async def handle_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ Siz admin emassiz.")
        return

    if query.data == "add_movie":
        await query.edit_message_text("🎬 Kino kodini va linkini quyidagicha yuboring:\n\n`kod = link`", parse_mode="Markdown")
        context.user_data["mode"] = "add_movie"
    elif query.data == "add_channel":
        await query.edit_message_text("➕ Kanal username'ni yuboring (masalan, `@yangi_kanal`):", parse_mode="Markdown")
        context.user_data["mode"] = "add_channel"

async def handle_admin_input(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    mode = context.user_data.get("mode")
    text = update.message.text

    if mode == "add_movie":
        if "=" not in text:
            await update.message.reply_text("❗ Format noto‘g‘ri. Quyidagicha bo‘lishi kerak:\n`kod = link`", parse_mode="Markdown")
            return
        code, link = [x.strip() for x in text.split("=", 1)]
        data = load_data()
        data[code] = link
        save_data(data)
        await update.message.reply_text(f"✅ Kino qo‘shildi:\n\n🎟 Kod: {code}\n🔗 Link: {link}")
        context.user_data["mode"] = None

    elif mode == "add_channel":
        if not text.startswith("@"):
            await update.message.reply_text("❗ Kanal username '@' bilan boshlanishi kerak.")
            return
        os.environ["CHANNEL_USERNAME"] = text
        await update.message.reply_text(f"✅ Kanal yangilandi: {text}")
        context.user_data["mode"] = None

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), handle_admin_input))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, lambda u, c: None))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, lambda u, c: None))
    app.add_handler(MessageHandler(filters.ALL, lambda u, c: None))
    app.add_handler(MessageHandler(filters.COMMAND, lambda u, c: None))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.ALL, lambda u, c: None))
    app.add_handler(MessageHandler(filters.StatusUpdate.CHAT_MEMBER, lambda u, c: None))
    app.add_handler(MessageHandler(filters.UpdateType.CALLBACK_QUERY, handle_buttons))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
