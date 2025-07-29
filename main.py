import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [6905227976]  # o'z telegram ID'ingizni bu yerga yozing

# Fayl nomlari
DATA_FILE = "data.json"
CHANNELS_FILE = "required_channels.json"
USERS_FILE = "users.json"

# JSON faylni o'qish yoki yaratish
def load_json(filename, default):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        with open(filename, 'w') as f:
            json.dump(default, f)
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Majburiy kanalga a'zolikni tekshirish
async def check_subscribed(user_id, context):
    channels = load_json(CHANNELS_FILE, [])
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                return False
        except:
            return False
    return True

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "foydalanuvchi"

    # Foydalanuvchini bazaga yozish
    users = load_json(USERS_FILE, [])
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

    if user_id in ADMIN_IDS:
        # Admin menyusi
        buttons = [
            [KeyboardButton("📥 Kino qo‘shish")],
            [KeyboardButton("➕ Kanal qo‘shish")],
            [KeyboardButton("📊 Statistika")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text(
            "Admin panelga xush kelibsiz!", reply_markup=reply_markup
        )
    else:
        # Oddiy foydalanuvchi
        subscribed = await check_subscribed(user_id, context)
        if not subscribed:
            channels = load_json(CHANNELS_FILE, [])
            btns = [[InlineKeyboardButton("➕ A'zo bo‘lish", url=f"https://t.me/{ch[1:]}")] for ch in channels]
            btns.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
            markup = InlineKeyboardMarkup(btns)
            await update.message.reply_text("Iltimos, quyidagi kanallarga a'zo bo‘ling:", reply_markup=markup)
            return

        await update.message.reply_text(f"Assalomu alaykum @{username}, botga xush kelibsiz!\n\n🎬 Kino kodini kiriting.")

# Inline tugma uchun qayta tekshirish
async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    subscribed = await check_subscribed(user_id, context)
    if subscribed:
        await query.edit_message_text("✅ Tabriklayman! Endi kino kodini yuboring.")
    else:
        await query.edit_message_text("🚫 Hali ham a'zo emassiz.")

# Kino kodini qayta ishlash
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        return  # admin menyu tugmalari uchun boshqa handler bor

    subscribed = await check_subscribed(user_id, context)
    if not subscribed:
        await update.message.reply_text("Iltimos, oldin kanalga a'zo bo‘ling.")
        return

    code = update.message.text.strip()
    data = load_json(DATA_FILE, {})

    if code in data:
        await update.message.reply_text("🎬 Mana siz so‘ragan kino:")
        await update.message.reply_document(document=data[code])
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

# Admin komandalar
admin_state = {}

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in ADMIN_IDS:
        return

    if text == "📥 Kino qo‘shish":
        admin_state[user_id] = "await_code"
        await update.message.reply_text("🎬 Kino kodi nima bo‘lsin?")
    elif text == "➕ Kanal qo‘shish":
        admin_state[user_id] = "await_channel"
        await update.message.reply_text("📣 Kanal username'ini yuboring (masalan: @kanalim)")
    elif text == "📊 Statistika":
        users = load_json(USERS_FILE, [])
        await update.message.reply_text(f"👤 Foydalanuvchilar soni: {len(users)}")

    elif user_id in admin_state:
        state = admin_state[user_id]

        if state == "await_code":
            context.user_data["new_code"] = text
            admin_state[user_id] = "await_file"
            await update.message.reply_text("📎 Endi faylni yuboring:")
        elif state == "await_file":
            if update.message.document:
                file_id = update.message.document.file_id
                code = context.user_data.get("new_code")
                data = load_json(DATA_FILE, {})
                data[code] = file_id
                save_json(DATA_FILE, data)
                await update.message.reply_text(f"✅ '{code}' kodi bilan saqlandi.")
                admin_state.pop(user_id)
            else:
                await update.message.reply_text("❌ Fayl yuboring.")
        elif state == "await_channel":
            channels = load_json(CHANNELS_FILE, [])
            if text.startswith("@"):
                if text not in channels:
                    channels.append(text)
                    save_json(CHANNELS_FILE, channels)
                    await update.message.reply_text(f"✅ {text} kanal majburiyga qo‘shildi.")
                else:
                    await update.message.reply_text("❗ Bu kanal allaqachon mavjud.")
            else:
                await update.message.reply_text("❌ Kanal username @ bilan boshlanishi kerak.")
            admin_state.pop(user_id)

# Botni ishga tushurish
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_IDS), handle_admin))
    app.add_handler(MessageHandler(filters.TEXT, handle_code))

    print("✅ Bot ishga tushdi!")
    app.run_polling()
