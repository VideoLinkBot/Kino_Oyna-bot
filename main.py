import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Fayllar
KINOLAR_FILE = "kinolar.json"
KANALLAR_FILE = "channels.json"
ADMIN_ID = 6905227976

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Fayl yuklash va saqlash
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# START komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🎥 Kino qo‘shish", callback_data="add_movie")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Admin panelga xush kelibsiz:", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("🎬 Kino kodini yuboring (masalan, 101):")

# Tugmalar uchun funksiyalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != ADMIN_ID:
        await query.edit_message_text("Sizda ruxsat yo‘q.")
        return

    if query.data == "add_movie":
        await query.edit_message_text(
            "Yangi kino qo‘shish uchun `kod|link` formatida yuboring.\n\nMasalan:\n101|https://t.me/yourchannel/123"
        )
        context.user_data["adding_movie"] = True

    elif query.data == "add_channel":
        await query.edit_message_text("Kanal usernameni kiriting (masalan: `@kanalim`):")
        context.user_data["adding_channel"] = True

    elif query.data == "stats":
        movies = load_json(KINOLAR_FILE)
        count = len(movies)
        await query.edit_message_text(f"📊 Bazadagi kinolar soni: {count} ta")

# Xabarlar uchun
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    movies = load_json(KINOLAR_FILE)

    # Kanal qo‘shish
    if user_id == ADMIN_ID and context.user_data.get("adding_channel"):
        kanallar = load_json(KANALLAR_FILE)
        if text in kanallar:
            await update.message.reply_text("⚠️ Bu kanal allaqachon mavjud.")
        else:
            kanallar.append(text)
            save_json(KANALLAR_FILE, kanallar)
            await update.message.reply_text(f"✅ Kanal qo‘shildi: {text}")
        context.user_data["adding_channel"] = False
        return

    # Kino qo‘shish
    if user_id == ADMIN_ID and context.user_data.get("adding_movie"):
        try:
            code, link = text.split("|")
            code = code.strip()
            link = link.strip()
            movies[code] = link
            save_json(KINOLAR_FILE, movies)
            await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo‘shildi: {code}")
        except Exception:
            await update.message.reply_text("❌ Noto‘g‘ri format. `kod|link` kiriting.")
        context.user_data["adding_movie"] = False
        return

    # Kino qidirish
    if text in movies:
        await update.message.reply_text(f"🎬 Kino topildi:\n{movies[text]}")
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi.")

# Dastur boshlanishi
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: BOT_TOKEN topilmadi.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
