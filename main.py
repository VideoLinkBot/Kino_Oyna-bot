import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def load_movies():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Menga kino kodini yuboring (masalan: KINO001)")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    movies = load_movies()
    if code in movies:
        movie = movies[code]
        caption = f"🎬 *{movie['title']}*\n📝 {movie['description']}"
        await update.message.reply_video(
            video=movie["video_id"],
            caption=caption,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Bunday kod bo‘yicha kino topilmadi.")

def main():
    app = ApplicationBuilder().token
