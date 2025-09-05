import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
CHANNELS = ["@kanal1", "@kanal2"]  # Majburiy obuna kanallari
DATA_FILE = "data.json"

# Obuna tekshirish
async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE):
    for ch in CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        buttons = [[InlineKeyboardButton(f"➕ Obuna bo‘lish {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
        buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        await update.message.reply_text(
            "❌ Kanallarga obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    await update.message.reply_text("✅ Xush kelibsiz! Kod kiriting (masalan: 100).")

# Tekshirish tugmasi
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if await check_subscription(user_id, context):
        await query.edit_message_text("✅ Obuna tasdiqlandi. Endi kod kiriting.")
    else:
        buttons = [[InlineKeyboardButton(f"➕ Obuna bo‘lish {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
        buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        await query.edit_message_text(
            "❌ Hali obuna bo‘lmadingiz:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Kino qo‘shish (admin)
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Foydalanish: /add <kod> <kanal_username> <message_id>")
        return
    code, channel, msg_id = args
    if not msg_id.isdigit():
        await update.message.reply_text("❗ Message ID raqam bo‘lishi kerak.")
        return
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[code] = {"channel": channel, "message_id": int(msg_id)}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
    await update.message.reply_text(f"✅ Kino kod {code} bilan qo‘shildi.")

# Foydalanuvchi kodi orqali kino olish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        buttons = [[InlineKeyboardButton(f"➕ Obuna bo‘lish {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
        buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        await update.message.reply_text(
            "❌ Avval kanallarga obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    code = update.message.text.strip()
    if not code.isdigit():
        await update.message.reply_text("❗ Faqat raqamli kod kiriting.")
        return
    if not os.path.exists(DATA_FILE):
        await update.message.reply_text("📂 Hech qanday kino mavjud emas.")
        return
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    if code not in data:
        await update.message.reply_text("❌ Bu kod bo‘yicha kino topilmadi.")
        return
    channel = data[code]["channel"]
    msg_id = data[code]["message_id"]
    try:
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=channel,
            message_id=msg_id
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik: {e}")

# Main
def main():
    PORT = int(os.environ.get("PORT", "8443"))
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_movie))
    app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))

    print("🤖 Bot ishga tushdi...")

    # Render webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://YOUR-RENDER-SUBDOMAIN.onrender.com/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
