import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# JSON file nomi
DATA_FILE = "data.json"

# Kino saqlash funksiyasi
def save_file_id(title, file_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[title] = file_id

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Kino olish funksiyasi
def load_file_id(title):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data.get(title)
    return None

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(f"Assalomu alaykum {name}, bizning botimizga xush kelibsiz!")

# Video qabul qilish
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    if video:
        title = update.message.caption or "unknown"
        file_id = video.file_id
        save_file_id(title, file_id)
        await update.message.reply_text(f"✅ Kino saqlandi: {title}")

# Kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        title = " ".join(context.args)
        file_id = load_file_id(title)
        if file_id:
            await update.message.reply_video(file_id)
        else:
            await update.message.reply_text("❌ Bunday nomli kino topilmadi.")
    else:
        await update.message.reply_text("Iltimos, kino nomini yozing. Masalan: `/kino Titanic`")

# Botni ishga tushirish
async def main():
    TOKEN = os.getenv("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kino", send_movie))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
