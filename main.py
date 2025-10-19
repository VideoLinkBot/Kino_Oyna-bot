#!/usr/bin/env python3
import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ----------------------
#  CONFIG (from .env)
# ----------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
# REQUIRED_CHANNELS: comma-separated list of @channelusernames or channel ids (e.g. @Kino_oyna1080,-100123..)
REQUIRED_CHANNELS = [ch.strip() for ch in os.getenv("REQUIRED_CHANNELS", "").split(",") if ch.strip()]

# ----------------------
#  FILES (persistence)
# ----------------------
KINO_DB_FILE = "kino_db.json"    # stores mapping: code -> {"type":"file"|"channel", ...}
STATS_FILE = "stats.json"        # stores views and daily subscribers (simple)

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

kino_db = load_json(KINO_DB_FILE, {})   # e.g. "100": {"type":"file","file_id":"ABC"}
stats = load_json(STATS_FILE, {"views": {}, "daily_users": {}})

# ----------------------
#  HELPERS
# ----------------------
async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # If no required channels -> treat as always subscribed
    if not REQUIRED_CHANNELS:
        return True
    for ch in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except Exception:
            # if API error (bad channel, bot not admin, etc.) treat as not subscribed
            return False
    return True

def increment_view(code: str, user_id: int):
    # total views per code
    stats["views"][code] = stats["views"].get(code, 0) + 1
    # daily unique users
    today = date.today().isoformat()
    if today not in stats["daily_users"]:
        stats["daily_users"][today] = []
    # store unique users for today
    if user_id not in stats["daily_users"][today]:
        stats["daily_users"][today].append(user_id)
    save_json(STATS_FILE, stats)

# ----------------------
#  COMMANDS (Admin + users)
# ----------------------

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == ADMIN_ID:
        kb = [
            [InlineKeyboardButton("➕ Add video (reply + /addvideo CODE)", callback_data="help_add")],
            [InlineKeyboardButton("📊 Stats", callback_data="show_stats")],
            [InlineKeyboardButton("📥 Add channel", callback_data="help_add_channel")],
        ]
        await update.message.reply_text("Admin panel:", reply_markup=InlineKeyboardMarkup(kb))
    else:
        # for users, instruct
        await update.message.reply_text("Salom! Kino kodi yuboring (masalan: 100).")

# Admin: addvideo by replying to a video: reply to the video message with command: /addvideo CODE
async def addvideo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != ADMIN_ID:
        return
    # If command is reply to a video message:
    if update.message.reply_to_message and update.message.reply_to_message.video:
        if not context.args:
            await update.message.reply_text("❗ Kodni yozing: /addvideo 100 (komandani videoga javob qilib yuboring)")
            return
        code = context.args[0].strip()
        video = update.message.reply_to_message.video
        file_id = video.file_id
        kino_db[code] = {"type": "file", "file_id": file_id, "added_by": uid, "added_at": datetime.utcnow().isoformat()}
        save_json(KINO_DB_FILE, kino_db)
        await update.message.reply_text(f"✅ Video qo'shildi. Kod: {code}")
        return

    # Or admin can add by specifying channel + message_id: /addvideo CODE @channel 123
    if len(context.args) >= 3:
        code = context.args[0].strip()
        ch = context.args[1].strip()
        try:
            msg_id = int(context.args[2])
        except:
            await update.message.reply_text("❗ Xato: message_id butun son bo'lishi kerak")
            return
        kino_db[code] = {"type": "channel", "chat_id": ch, "message_id": msg_id, "added_by": uid, "added_at": datetime.utcnow().isoformat()}
        save_json(KINO_DB_FILE, kino_db)
        await update.message.reply_text(f"✅ Kanal post sifatida qo'shildi. Kod: {code}")
        return

    await update.message.reply_text("❗ Foydalanish:\n • Reply qilib: /addvideo 100  (videoga javob qilib komanda yuboring)\n • Yoki: /addvideo 100 @channel MESSAGE_ID")

# Admin: remove video
async def removevideo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /removevideo 100")
        return
    code = context.args[0].strip()
    if code in kino_db:
        kino_db.pop(code)
        save_json(KINO_DB_FILE, kino_db)
        await update.message.reply_text(f"✅ {code} o‘chirildi.")
    else:
        await update.message.reply_text("❗ Bunday kod topilmadi.")

# Admin: show stats
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total_codes = len(kino_db)
    text = f"📊 Statistika:\n • Kinolar: {total_codes}\n\nKo‘rilishlar (top 20):\n"
    top = sorted(stats.get("views", {}).items(), key=lambda x: x[1], reverse=True)[:20]
    if top:
        for code, cnt in top:
            text += f"   • {code} — {cnt}\n"
    else:
        text += "   — Hozircha yo‘q\n"
    # today subscribers added (if REQUIRED_CHANNELS used, we cannot know new subs; we track daily_users)
    today = date.today().isoformat()
    todays = len(stats.get("daily_users", {}).get(today, []))
    text += f"\nBugun botdan kinolarni so‘ragan noyob foydalanuvchilar: {todays}\n"
    await update.message.reply_text(text)

# Admin: add required channel to env variable at runtime (stored in memory only)
async def addchannel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /addchannel @channelname")
        return
    ch = context.args[0].strip()
    if ch not in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.append(ch)
        await update.message.reply_text(f"✅ Kanal qo'shildi: {ch}")
    else:
        await update.message.reply_text("🔁 Kanal allaqachon ro'yxatda.")

async def removechannel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /removechannel @channelname")
        return
    ch = context.args[0].strip()
    if ch in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.remove(ch)
        await update.message.reply_text(f"❌ Kanal olib tashlandi: {ch}")
    else:
        await update.message.reply_text("❗ Kanal topilmadi ro'yxatda.")

# User sends a code (text)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    # first check subscription
    if not await is_user_subscribed(user_id, context):
        # show buttons to subscribe
        kb = []
        for ch in REQUIRED_CHANNELS:
            chname = ch.lstrip("@")
            kb.append([InlineKeyboardButton(f"Obuna — {ch}", url=f"https://t.me/{chname}")])
        kb.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        await update.message.reply_text("🔒 Botdan foydalanish uchun avval kanal(lar)ga obuna bo'ling:", reply_markup=InlineKeyboardMarkup(kb))
        return

    code = text
    item = kino_db.get(code)
    if not item:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")
        return

    # send the video:
    try:
        if item["type"] == "file":
            # send by file_id
            file_id = item["file_id"]
            await context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)
        elif item["type"] == "channel":
            # copy message from channel post to user
            from_chat = item["chat_id"]
            msg_id = item["message_id"]
            await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=from_chat, message_id=msg_id)
        # stats
        increment_view(code, user_id)
    except Exception as e:
        await update.message.reply_text("❗ Video yuborishda xato yuz berdi.")
        print("Error sending video:", e)

# Callback: check subscription
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_sub":
        user_id = query.from_user.id
        if await is_user_subscribed(user_id, context):
            await query.edit_message_text("✅ Obuna tasdiqlandi. Kod yuboring.")
        else:
            await query.edit_message_text("❌ Hali ham obuna emassiz. Iltimos qayta obuna bo'ling.")

# ----------------------
#  SETUP & RUN
# ----------------------
def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set in .env")
        return
    app = Application.builder().token(BOT_TOKEN).build()

    # basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addvideo", addvideo_cmd))        # admin add by reply or channel msg
    app.add_handler(CommandHandler("removevideo", removevideo_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("addchannel", addchannel_cmd))
    app.add_handler(CommandHandler("removechannel", removechannel_cmd))

    app.add_handler(CallbackQueryHandler(callback_query_handler, pattern="^check_sub$"))
    # text handler for codes
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
