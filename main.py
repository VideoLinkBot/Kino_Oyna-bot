import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import json
import os

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [6905227976]  # o‘zingizning Telegram IDingizni yozing

# Fayllar
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
KINOLAR_FILE = "kinolar.json"

# Yordamchi funksiya: JSON o‘qish va yozish
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    # Foydalanuvchini saqlaymiz
    users = load_json(USERS_FILE)
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

    # Kanal tekshiruvi
    channels = load_json(CHANNELS_FILE)
    if channels:
        buttons = [[InlineKeyboardButton("✅ Kanalga obuna bo‘ldim", callback_data="check_subs")]]
        for ch in channels:
            buttons.insert(0, [InlineKeyboardButton(f"➕ {ch['name']}", url=f"https://t.me/{ch['username']}")])
        await update.message.reply_text("⛔ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(f"Assalomu alaykum, {first_name}! 👋\nKino kodini kiriting.")

# Obuna tekshirish
async def check_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    channels = load_json(CHANNELS_FILE)
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{ch['username']}", user_id=user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                await query.message.reply_text("❌ Hali hamma kanallarga obuna bo‘lmadingiz.")
                return
        except Exception:
            await query.message.reply_text("⚠ Kanal topilmadi yoki xatolik yuz berdi.")
            return

    await query.message.reply_text("✅ Raxmat! Endi kino kodini yuboring.")

# Kino yuborish
async def kino_qidirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    matn = update.message.text.strip()

    kinolar = load_json(KINOLAR_FILE)
    kino = next((k for k in kinolar if k['kod'] == matn), None)
    if kino:
        await update.message.reply_video(video=kino['video_id'], caption=f"🎬 {kino['name']}")
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

# Admin panel
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Siz admin emassiz.")
    
    buttons = [
        [InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel")],
        [InlineKeyboardButton("🎬 Kino qo‘shish", callback_data="add_kino")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
    ]
    await update.message.reply_text("🔧 Admin panel", reply_markup=InlineKeyboardMarkup(buttons))

# Callback uchun ishlovchi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        return await query.message.reply_text("⛔ Siz admin emassiz.")

    if query.data == "add_channel":
        context.user_data['add_channel'] = True
        await query.message.reply_text("📢 Kanal username va nomini yozing (masalan: `mychannel KinoUz`)")
    elif query.data == "add_kino":
        context.user_data['add_kino'] = True
        await query.message.reply_text("🎬 Kino kodini, nomini va video ID ni yozing (masalan: `500 Kino nomi BAChF3r...`)")
    elif query.data == "stats":
        users = load_json(USERS_FILE)
        kinolar = load_json(KINOLAR_FILE)
        await query.message.reply_text(f"📊 Statistika:\n👥 Foydalanuvchilar: {len(users)}\n🎬 Kinolar soni: {len(kinolar)}")

# Kino va kanal qo‘shish
async def add_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Kanal qo‘shish
    if context.user_data.get('add_channel'):
        try:
            username, name = text.split()
            channels = load_json(CHANNELS_FILE)
            channels.append({"username": username.lstrip("@"), "name": name})
            save_json(CHANNELS_FILE, channels)
            await update.message.reply_text("✅ Kanal qo‘shildi.")
        except:
            await update.message.reply_text("⚠ Format noto‘g‘ri. `mychannel KinoUz` kabi yozing.")
        context.user_data['add_channel'] = False

    # Kino qo‘shish
    elif context.user_data.get('add_kino'):
        try:
            kod, name, video_id = text.split(maxsplit=2)
            kinolar = load_json(KINOLAR_FILE)
            kinolar.append({"kod": kod, "name": name, "video_id": video_id})
            save_json(KINOLAR_FILE, kinolar)
            await update.message.reply_text("✅ Kino qo‘shildi.")
        except:
            await update.message.reply_text("⚠ Format noto‘g‘ri. `500 Kino nomi BAChF...` kabi yozing.")
        context.user_data['add_kino'] = False

# Asosiy run qismi
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kino_qidirish))

    print("✅ Bot ishga tushdi!")
    app.run_polling()import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import json
import os

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [123456789]  # o‘zingizning Telegram IDingizni yozing

# Fayllar
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
KINOLAR_FILE = "kinolar.json"

# Yordamchi funksiya: JSON o‘qish va yozish
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    # Foydalanuvchini saqlaymiz
    users = load_json(USERS_FILE)
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

    # Kanal tekshiruvi
    channels = load_json(CHANNELS_FILE)
    if channels:
        buttons = [[InlineKeyboardButton("✅ Kanalga obuna bo‘ldim", callback_data="check_subs")]]
        for ch in channels:
            buttons.insert(0, [InlineKeyboardButton(f"➕ {ch['name']}", url=f"https://t.me/{ch['username']}")])
        await update.message.reply_text("⛔ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(f"Assalomu alaykum, {first_name}! 👋\nKino kodini kiriting.")

# Obuna tekshirish
async def check_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    channels = load_json(CHANNELS_FILE)
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{ch['username']}", user_id=user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                await query.message.reply_text("❌ Hali hamma kanallarga obuna bo‘lmadingiz.")
                return
        except Exception:
            await query.message.reply_text("⚠ Kanal topilmadi yoki xatolik yuz berdi.")
            return

    await query.message.reply_text("✅ Raxmat! Endi kino kodini yuboring.")

# Kino yuborish
async def kino_qidirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    matn = update.message.text.strip()

    kinolar = load_json(KINOLAR_FILE)
    kino = next((k for k in kinolar if k['kod'] == matn), None)
    if kino:
        await update.message.reply_video(video=kino['video_id'], caption=f"🎬 {kino['name']}")
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

# Admin panel
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Siz admin emassiz.")
    
    buttons = [
        [InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel")],
        [InlineKeyboardButton("🎬 Kino qo‘shish", callback_data="add_kino")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
    ]
    await update.message.reply_text("🔧 Admin panel", reply_markup=InlineKeyboardMarkup(buttons))

# Callback uchun ishlovchi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        return await query.message.reply_text("⛔ Siz admin emassiz.")

    if query.data == "add_channel":
        context.user_data['add_channel'] = True
        await query.message.reply_text("📢 Kanal username va nomini yozing (masalan: `mychannel KinoUz`)")
    elif query.data == "add_kino":
        context.user_data['add_kino'] = True
        await query.message.reply_text("🎬 Kino kodini, nomini va video ID ni yozing (masalan: `500 Kino nomi BAChF3r...`)")
    elif query.data == "stats":
        users = load_json(USERS_FILE)
        kinolar = load_json(KINOLAR_FILE)
        await query.message.reply_text(f"📊 Statistika:\n👥 Foydalanuvchilar: {len(users)}\n🎬 Kinolar soni: {len(kinolar)}")

# Kino va kanal qo‘shish
async def add_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Kanal qo‘shish
    if context.user_data.get('add_channel'):
        try:
            username, name = text.split()
            channels = load_json(CHANNELS_FILE)
            channels.append({"username": username.lstrip("@"), "name": name})
            save_json(CHANNELS_FILE, channels)
            await update.message.reply_text("✅ Kanal qo‘shildi.")
        except:
            await update.message.reply_text("⚠ Format noto‘g‘ri. `mychannel KinoUz` kabi yozing.")
        context.user_data['add_channel'] = False

    # Kino qo‘shish
    elif context.user_data.get('add_kino'):
        try:
            kod, name, video_id = text.split(maxsplit=2)
            kinolar = load_json(KINOLAR_FILE)
            kinolar.append({"kod": kod, "name": name, "video_id": video_id})
            save_json(KINOLAR_FILE, kinolar)
            await update.message.reply_text("✅ Kino qo‘shildi.")
        except:
            await update.message.reply_text("⚠ Format noto‘g‘ri. `500 Kino nomi BAChF...` kabi yozing.")
        context.user_data['add_kino'] = False

# Asosiy run qismi
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kino_qidirish))

    print("✅ Bot ishga tushdi!")
    app.run_polling()
