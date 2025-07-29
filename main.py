import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === 🔑 Sozlamalar ===
BOT_TOKEN = "8163580969:AAG3HoJAXJH9OeQQ79b51qPtQO75KHTZBZY"
ADMIN_ID = 6905227976

# === 📂 Ma'lumotlar
kino_data = {}
channels = []
users = {}
code_stats = {}

def load_data():
    global kino_data, channels, users, code_stats
    try: kino_data.update(json.load(open("kino_data.json", "r", encoding="utf-8")))
    except: pass
    try: channels.extend(json.load(open("channels.json", "r", encoding="utf-8")))
    except: pass
    try: users.update(json.load(open("users.json", "r", encoding="utf-8")))
    except: pass
    try: code_stats.update(json.load(open("code_stats.json", "r", encoding="utf-8")))
    except: pass

def save_all():
    json.dump(kino_data, open("kino_data.json", "w", encoding="utf-8"), indent=2)
    json.dump(channels, open("channels.json", "w", encoding="utf-8"), indent=2)
    json.dump(users, open("users.json", "w", encoding="utf-8"), indent=2)
    json.dump(code_stats, open("code_stats.json", "w", encoding="utf-8"), indent=2)

async def check_subscription(user_id, context):
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# === /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        await update.message.reply_text("📛 Iltimos, botdan foydalanish uchun kanal(lar)ga obuna bo‘ling.")
        return
    await update.message.reply_text("🎬 Salom! Kod yuboring. Masalan: 100")

# === Kino kodi
async def send_kino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    kod = update.message.text.strip()
    if not await check_subscription(user_id, context):
        await update.message.reply_text("📛 Avval kanal(lar)ga obuna bo‘ling.")
        return
    if kod in kino_data:
        await update.message.reply_text(f"🎥 Kino: {kino_data[kod]}")
        users[str(user_id)] = users.get(str(user_id), 0) + 1
        code_stats[kod] = code_stats.get(kod, 0) + 1
        save_all()
    else:
        await update.message.reply_text("🚫 Bunday kod topilmadi.")

# === /add
async def add_kino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        kod, link = context.args[0], context.args[1]
        kino_data[kod] = link
        save_all()
        await update.message.reply_text(f"✅ Qo‘shildi: {kod}")
    except:
        await update.message.reply_text("❌ Foydalanish: /add 100 https://t.me/link")

# === /delete
async def delete_kino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        kod = context.args[0]
        if kod in kino_data:
            kino_data.pop(kod)
            save_all()
            await update.message.reply_text(f"🗑 O‘chirildi: {kod}")
        else:
            await update.message.reply_text("❌ Kod topilmadi.")
    except:
        await update.message.reply_text("❌ Namuna: /delete 100")

# === /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total_users = len(users)
    total_codes = len(kino_data)
    top_codes = sorted(code_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    text = f"📊 Statistika:\n👥 Foydalanuvchilar: {total_users}\n🎞 Kinolar: {total_codes}\n\nEng ko‘p ishlatilgan kodlar:\n"
    for kod, soni in top_codes:
        text += f"🔹 {kod} — {soni} marta\n"
    await update.message.reply_text(text)

# === /setchannels
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global channels
    channels = context.args[:10]
    save_all()
    await update.message.reply_text("✅ Kanallar yangilandi.")

# === /removechannels
async def remove_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global channels
    channels = []
    save_all()
    await update.message.reply_text("✅ Barcha kanallar olib tashlandi.")

# === Ishga tushirish
def main():
    load_data()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_kino))
    app.add_handler(CommandHandler("delete", delete_kino))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("setchannels", set_channels))
    app.add_handler(CommandHandler("removechannels", remove_channels))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_kino))
    print("🤖 Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
