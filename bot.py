import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Kino bazasini yuklaymiz
def load_movies():
    with open("movies.json", "r", encoding="utf-8") as file:
        return json.load(file)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 Salom! Menga kino kodini yuboring (masalan: KINO001)")

# Kod orqali kinoni topish
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    movies = load_movies()

    if code in movies:
        movie = movies[code]
        caption = f"🎬 *{movie['title']}*\n📝 {movie['description']}"
        await update.message.reply_video(
            video=movie['video_id'],
            caption=caption,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Kechirasiz, bu kod bo‘yicha kino topilmadi.")

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token("8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
