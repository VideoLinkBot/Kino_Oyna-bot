import json
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# 🎯 O'ZGARTIRING: Bu yerga sizning bot tokeningiz
BOT_TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"

# 🎯 O'ZGARTIRING: Bu yerga sizning kanal username'ingiz
CHANNEL_USERNAME = "@AlTarjimonUz_Bot"

# Har bir foydalanuvchi uchun holatni eslab qolish
user_states = {}

# JSON ma'lumotlarni o'qish
def load_db():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# JSON ma'lumotlarni yozish
def save_db(db):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_states[user.id] = {"subscribed": False}
    await update.message.reply_text(
        f"Assalomu alaykum, @{user.username}!\n"
        "Xush kelibsiz! Iltimos, kino kodini kiriting."
    )

# Kanalga obuna bo‘lganmi - tekshiruv
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]

# Kodlar va kino yuborish funksiyasi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 1. Obuna holatini tekshiramiz
    if user_id not in user_states or not user_states[user_id]["subscribed"]:
        subscribed = await check_subscription(update, context)
        if not subscribed:
            await update.message.reply_text(
                "❗ Uzr, kinoni ko‘rishdan oldin kanalimizga obuna bo‘ling:\n➕ @AlTarjimonUz_Bot"
            )
            return
        else:
            user_states[user_id] = {"subscribed": True}
            await update.message.reply_text(
                "✅ Obuna tasdiqlandi. Endi kino kodini qayta yuboring."
            )
            return

    # 2. Kodni tekshirib, ma'lumotni yuboramiz
    db = load_db()
    code = text.upper()  # BZ01, BZ02 holatda bo'ladi
    if code in db:
        db[code]["views"] += 1
        save_db(db)
        film = db[code]
        await update.message.reply_text(
            f"🎬 Kino: {film['name']}\n🎭 Janr: {film['genre']}\n👁 Ko‘rilgan: {film['views']} marta"
        )
        if "file_id" in film:
            await update.message.reply_video(film["file_id"])
    else:
        await update.message.reply_text("❗ Bunday kod topilmadi.")
    

# Botni ishga tushirish
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
