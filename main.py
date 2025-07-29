import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"

KANAL_NOMI, KANAL_IDSI, KINO_KODI = range(3)

asosiy_tugma = [["🎬 Kino qo‘shish", "📊 Statistika"], ["➕ Kanal qo‘shish"]]

# Foydalanuvchi kinoni qo‘shmoqda degan belgini saqlaymiz
KINO_FILE = "kinolar.json"

def kanalni_saqlash(nomi, idsi):
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"kanallar": []}

    data["kanallar"].append({"nomi": nomi, "id": idsi})

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def kino_saqlash(kod, link):
    try:
        with open(KINO_FILE, "r") as f:
            kinolar = json.load(f)
    except FileNotFoundError:
        kinolar = {}

    kinolar[kod] = link

    with open(KINO_FILE, "w") as f:
        json.dump(kinolar, f, indent=4)

def kino_soni():
    try:
        with open(KINO_FILE, "r") as f:
            kinolar = json.load(f)
        return len(kinolar)
    except FileNotFoundError:
        return 0

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Quyidagi tugmalardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(asosiy_tugma, resize_keyboard=True)
    )

# Tugmalarni boshqarish
async def tugma_bosildi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "➕ Kanal qo‘shish":
        await update.message.reply_text("Kanal nomini kiriting:")
        return KANAL_NOMI

    elif text == "🎬 Kino qo‘shish":
        await update.message.reply_text("Kino kodini kiriting (`kod|link`):")
        return KINO_KODI

    elif text == "📊 Statistika":
        soni = kino_soni()
        await update.message.reply_text(f"📊 Bazada {soni} ta kino mavjud.")
        return ConversationHandler.END

    else:
        await update.message.reply_text("Iltimos, menyudagi tugmalardan foydalaning.")
        return ConversationHandler.END

# Kanal nomi
async def kanal_nomi_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kanal_nomi"] = update.message.text
    await update.message.reply_text("Endi kanal ID raqamini kiriting:")
    return KANAL_IDSI

# Kanal ID
async def kanal_id_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kanal_idsi = update.message.text
    kanal_nomi = context.user_data["kanal_nomi"]
    kanalni_saqlash(kanal_nomi, kanal_idsi)

    await update.message.reply_text(f"✅ Kanal qo‘shildi:\n📺 {kanal_nomi} — 🆔 {kanal_idsi}")
    return ConversationHandler.END

# Kino qo‘shish
async def kino_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = update.message.text
    if "|" in matn:
        kod, link = matn.split("|", 1)
        kod = kod.strip()
        link = link.strip()
        kino_saqlash(kod, link)
        await update.message.reply_text(f"✅ Kino qo‘shildi: {kod}")
    else:
        await update.message.reply_text("❌ Format noto‘g‘ri. Iltimos `kod|link` tarzida kiriting.")
    return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    kino_conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎬 Kino qo‘shish$"), tugma_bosildi)],
        states={KINO_KODI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kino_qabul)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    kanal_conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Kanal qo‘shish$"), tugma_bosildi)],
        states={
            KANAL_NOMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_nomi_qabul)],
            KANAL_IDSI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_id_qabul)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(kino_conversation)
    app.add_handler(kanal_conversation)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tugma_bosildi))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
