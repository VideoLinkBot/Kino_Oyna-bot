from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, ConversationHandler
)
import json
import os
import asyncio

TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"  # ← O'zingizning TOKEN'ingiz
ADMIN_ID = 6905227976

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

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users = load_json(FOYDALANUVCHILAR_FILE)
    if user_id not in users:
        users.append(user_id)
        save_json(FOYDALANUVCHILAR_FILE, users)

    keyboard = [
        [KeyboardButton("🎥 Kino qo‘shish")],
        [KeyboardButton("📊 Statistika")],
        [KeyboardButton("➕ Kanal qo‘shish")]
    ]
    await update.message.reply_text("Asosiy menyu:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def kanal_qoshish(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return await update.message.reply_text("Faqat admin kanal qo‘sha oladi.")
    
    await update.message.reply_text("Kanal usernameni yuboring (masalan: @kinolar)")
    return 1

async def kanal_saqlash(update: Update, context: CallbackContext):
    kanal = update.message.text.strip()
    kanallar = load_json(KANALLAR_FILE)
    if kanal not in kanallar:
        kanallar.append(kanal)
        save_json(KANALLAR_FILE, kanallar)
        await update.message.reply_text("✅ Kanal qo‘shildi.")
    else:
        await update.message.reply_text("⚠️ Bu kanal allaqachon qo‘shilgan.")
    return ConversationHandler.END

async def statistika(update: Update, context: CallbackContext):
    users = load_json(FOYDALANUVCHILAR_FILE)
    await update.message.reply_text(f"👥 Foydalanuvchilar soni: {len(users)}")

async def kino_qoshish(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    kanallar = load_json(KANALLAR_FILE)

    for kanal in kanallar:
        try:
            member = await context.bot.get_chat_member(kanal, user_id)
            if member.status in ["left", "kicked"]:
                raise Exception("Obuna emas")
        except:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{kanal[1:]}")]])
            await update.message.reply_text(f"Iltimos, kanalga obuna bo‘ling: {kanal}", reply_markup=btn)
            return ConversationHandler.END

    await update.message.reply_text("🎬 Kino kodini yuboring:")
    return 2

async def kino_saqlash(update: Update, context: CallbackContext):
    kod = update.message.text.strip()
    kinolar = load_json(KINO_FILE)
    if kod not in kinolar:
        kinolar.append(kod)
        save_json(KINO_FILE, kinolar)
        await update.message.reply_text("✅ Kino saqlandi.")
    else:
        await update.message.reply_text("⚠️ Bu kod allaqachon mavjud.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📊 Statistika$"), statistika))

    # Kanal qo'sish
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Kanal qo‘shish$"), kanal_qoshish)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_saqlash)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    # Kino qo'sish
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎥 Kino qo‘shish$"), kino_qoshish)],
        states={2: [MessageHandler(filters.TEXT & ~filters.COMMAND, kino_saqlash)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
