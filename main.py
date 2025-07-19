import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "BOT_TOKENINGNI_BU_YERGA_YOZ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = user.full_name
    await update.message.reply_text(f"Assalamu alaykum {full_name}, botimizga xush kelibsiz!\nKodni kiriting, men sizga kinoni chiqarib beraman.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if user_input in data:
            file_id = data[user_input]
            await context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)
        else:
            await update.message.reply_text("❌ Bunday kod topilmadi. Kodni to‘g‘ri kiriting.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
