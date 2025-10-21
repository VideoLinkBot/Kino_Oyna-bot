import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎬 Assalomu alaykum, {user.first_name}!\n"
        "Kino_Oyna botimizga xush kelibsiz!\n\n"
        "🎥 Kino kodini kiriting (masalan, 130) — va biz sizga kinoni yuboramiz!"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
