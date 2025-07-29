import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"

KANAL_NOMI, KANAL_IDSI = range(2)

# Tugmalar
asosiy_tugma = [["🎬 Kino qo‘shish", "📊 Statistika"], ["➕ Kanal qo‘shish"]]

# JSONga yozish
def kanalni_saqlash(nomi, idsi):
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"kanallar": []}

    data["kanallar"].append({"nomi": nomi, "id": idsi})

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Quyidagi tugmalardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(asosiy_tugma, resize_keyboard=True)
    )

# Tugma bosilganda
async def tugma_bosildi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "➕ Kanal qo‘shish":
        await update.message.reply_text("Kanal nomini kiriting:")
        return KANAL_NOMI

    elif text == "🎬 Kino qo‘shish":
        await update.message.reply_text("❗ Kino qo‘shish funksiyasi hozircha faollashtirilmagan.")
        return ConversationHandler.END

    elif text == "📊 Statistika":
        await update.message.reply_text("❗ Statistika funksiyasi hozircha mavjud emas.")
        return ConversationHandler.END

    else:
        await update.message.reply_text("Iltimos, menyudan tugmani tanlang.")
        return ConversationHandler.END

# Kanal nomi qabul qilish
async def kanal_nomi_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kanal_nomi"] = update.message.text
    await update.message.reply_text("Endi kanal ID raqamini kiriting:")
    return KANAL_IDSI

# Kanal ID qabul qilish va saqlash
async def kanal_id_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kanal_idsi = update.message.text
    kanal_nomi = context.user_data["kanal_nomi"]

    kanalni_saqlash(kanal_nomi, kanal_idsi)

    await update.message.reply_text(f"✅ Kanal muvaffaqiyatli qo‘shildi:\n📺 Nomi: {kanal_nomi}\n🆔 ID: {kanal_idsi}")
    return ConversationHandler.END

# Cancel holati
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

# Botni ishga tushirish
def main():
    app = Application.builder().token(TOKEN).build()

    kanal_qoshish = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Kanal qo‘shish$"), tugma_bosildi)],
        states={
            KANAL_NOMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_nomi_qabul)],
            KANAL_IDSI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_id_qabul)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(kanal_qoshish)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tugma_bosildi))

    app.run_polling()

if __name__ == "__main__":
    main()
