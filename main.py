import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest

# 🔐 Admin Telegram ID
ADMIN_ID = 6905227976

# 📢 Obuna shart bo‘lgan kanallar
obuna_kanallari = [
    "YOURCHANNEL1",  # Faqat username, masalan: "Kino_Oyna1080p"
    "YOURCHANNEL2",
]

# 📁 Kino bazasi
KINOLAR_FILE = "kinolar.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🎬 Kino yuklash
def load_movies():
    if os.path.exists(KINOLAR_FILE):
        with open(KINOLAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 💾 Kino saqlash
def save_movies(data):
    with open(KINOLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 📛 Obuna tekshiruvchi
async def check_subscription(user_id, context):
    for channel in obuna_kanallari:
        try:
            member = await context.bot.get_chat_member(f"@{channel}", user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except BadRequest:
            return False
    return True

# ▶️ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{obuna_kanallari[0]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")],
        ]
        await update.message.reply_text(
            "❗ Botdan foydalanish uchun kanalga obuna bo‘ling.", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        ]
        await update.message.reply_text("Admin panelga xush kelibsiz:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("🎬 Kino kodini yuboring (masalan, 101):")

# 🔁 Tugma (callback)lar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_subs":
        if await check_subscription(user_id, context):
            await query.edit_message_text("✅ Rahmat! Endi kino kodini yuboring.")
        else:
            await query.edit_message_text("❗ Hali ham obuna bo‘lmagansiz.")
        return

    if user_id != ADMIN_ID:
        await query.edit_message_text("Sizda ruxsat yo‘q.")
        return

    if query.data == "add_movie":
        await query.edit_message_text(
            "Yangi kino qo‘shish uchun `kod|link` formatida yuboring.\n\nMasalan:\n101|https://t.me/yourchannel/123"
        )
        context.user_data["adding_movie"] = True

    elif query.data == "stats":
        movies = load_movies()
        count = len(movies)
        await query.edit_message_text(f"📊 Bazadagi kinolar soni: {count} ta")

# 💬 Kino kodi yoki admindan kino qo‘shish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not await check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{obuna_kanallari[0]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")],
        ]
        await update.message.reply_text(
            "❗ Iltimos, botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    movies = load_movies()

    # Admin kino qo‘shyapti
    if user_id == ADMIN_ID and context.user_data.get("adding_movie"):
        try:
            code, link = text.split("|")
            code = code.strip()
            link = link.strip()
            movies[code] = link
            save_movies(movies)
            await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo‘shildi: {code}")
        except Exception:
            await update.message.reply_text("❌ Format noto‘g‘ri. `kod|link` bo‘lishi kerak.")
        context.user_data["adding_movie"] = False
        return

    # Oddiy foydalanuvchi kod yubordi
    if text in movies:
        await update.message.reply_text(f"🎬 Kino topildi:\n{movies[text]}")
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi. To‘g‘ri kod yuboring.")

# 🚀 Botni ishga tushirish
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        print("ERROR: BOT_TOKEN .env faylida yo‘q!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi...")
    app.run_polling()
