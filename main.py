from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import json
import os

TOKEN = "YOUR_BOT_TOKEN"  # <<< Bot tokenini shu yerga yoz
ADMIN_ID = 6905227976     # <<< Admin ID

KANALLAR_FILE = "channels.json"
KINO_FILE = "kino.json"
FOYDALANUVCHILAR_FILE = "users.json"

# Fayllar yo'q bo'lsa yaratamiz
for file in [KANALLAR_FILE, KINO_FILE, FOYDALANUVCHILAR_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users = load_json(FOYDALANUVCHILAR_FILE)
    if user_id not in users:
        users.append(user_id)
        save_json(FOYDALANUVCHILAR_FILE, users)

    keyboard = [
        [KeyboardButton("🎥 Kino qo‘shish"), KeyboardButton("📊 Statistika")],
        [KeyboardButton("➕ Kanal qo‘shish")]
    ]
    update.message.reply_text("Asosiy menyu:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def kanal_qoshish(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return update.message.reply_text("Faqat admin kanal qo‘sha oladi.")
    
    update.message.reply_text("Kanal usernameni yuboring (masalan: @kinolar)")
    return 1

def kanal_saqlash(update: Update, context: CallbackContext):
    kanal = update.message.text
    kanallar = load_json(KANALLAR_FILE)
    if kanal not in kanallar:
        kanallar.append(kanal)
        save_json(KANALLAR_FILE, kanallar)
        update.message.reply_text("✅ Kanal qo‘shildi.")
    else:
        update.message.reply_text("⚠️ Bu kanal allaqachon qo‘shilgan.")
    return ConversationHandler.END

def statistika(update: Update, context: CallbackContext):
    users = load_json(FOYDALANUVCHILAR_FILE)
    update.message.reply_text(f"👥 Foydalanuvchilar soni: {len(users)}")

def kino_qoshish(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    kanallar = load_json(KANALLAR_FILE)

    # Tekshirish
    for kanal in kanallar:
        try:
            member = context.bot.get_chat_member(kanal, user_id)
            if member.status in ["left", "kicked"]:
                raise Exception("Obuna emas")
        except:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{kanal[1:]}")]])
            update.message.reply_text(f"Iltimos, quyidagi kanalga obuna bo‘ling: {kanal}", reply_markup=btn)
            return

    update.message.reply_text("🎬 Kino kodini yuboring:")
    return 2

def kino_saqlash(update: Update, context: CallbackContext):
    kod = update.message.text
    kinolar = load_json(KINO_FILE)
    kinolar.append(kod)
    save_json(KINO_FILE, kinolar)
    update.message.reply_text("✅ Kino saqlandi.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📊 Statistika$"), statistika))
    app.add_handler(MessageHandler(filters.Regex("^🎥 Kino qo‘shish$"), kino_qoshish))
    
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Kanal qo‘shish$"), kanal_qoshish)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_saqlash)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎥 Kino qo‘shish$"), kino_qoshish)],
        states={2: [MessageHandler(filters.TEXT & ~filters.COMMAND, kino_saqlash)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
