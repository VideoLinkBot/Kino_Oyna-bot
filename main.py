import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# .env fayldan ma’lumotlarni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNELS = json.loads(os.getenv("CHANNELS_JSON"))  # ["@kanal1", "@kanal2"]

DATA_FILE = "data.json"
USERS_FILE = "users.json"

# Foydalanuvchi ID larni saqlash
def add_user(user_id: int):
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# Obuna tekshiruvi
async def check_subs(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    for ch in CHANNELS:
        member = await context.bot.get_chat_member(ch, user_id)
        if member.status in ["left", "kicked"]:
            return False
    return True

# Obuna bo‘lmaganlarga tugma yuborish
async def force_subscribe(update: Update):
    buttons = [
        [InlineKeyboardButton("✅ Obuna bo‘lish", url=f"https://t.me/{ch[1:]}")]
        for ch in CHANNELS
    ]
    buttons.append([InlineKeyboardButton("Tekshirish ✅", callback_data="check_subs")])
    await update.message.reply_text("Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=InlineKeyboardMarkup(buttons))

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    if await check_subs(user_id, context):
        await update.message.reply_text("🎬 Kod kiriting (masalan: 100)")
    else:
        await force_subscribe(update)

# Kod orqali kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subs(user_id, context):
        await force_subscribe(update)
        return

    code = update.message.text.strip()
    if not code.isdigit():
        await update.message.reply_text("❗️Faqat raqamli kod kiriting.")
        return

    if not os.path.exists(DATA_FILE):
        await update.message.reply_text("📂 Hech qanday kino mavjud emas.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if code not in data:
        await update.message.reply_text("❌ Bu kod bo‘yicha kino topilmadi.")
        return

    channel_username = data[code]["channel"]
    message_id = data[code]["message_id"]

    try:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=channel_username,
            message_id=message_id
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik: {e}")

# Admin: kino qo‘shish
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Foydalanish: /add <kod> <kanal_username> <message_id>")
        return

    code, channel, msg_id = args
    if not msg_id.isdigit():
        await update.message.reply_text("❗️Message ID raqam bo‘lishi kerak.")
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

# Admin: statistika
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)

    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    await update.message.reply_text(f"📊 Statistika:\n👤 Foydalanuvchilar: {len(users)}\n🎬 Kinolar: {len(data)}")

# Obuna qayta tekshirish
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if await check_subs(user_id, context):
        await query.message.delete()
        await query.message.reply_text("✅ Obuna tasdiqlandi. Endi kod kiriting.")
    else:
        await query.message.reply_text("🚫 Hali ham obuna bo‘lmagansiz.")

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_movie))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(check_button, pattern="check_subs"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
