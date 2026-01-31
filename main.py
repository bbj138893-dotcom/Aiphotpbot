import os
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===== START =====
@bot.message_handler(commands=["start"])
def start(m):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🧼 Remove Background", callback_data="bg"),
        InlineKeyboardButton("🔁 Face Swap", callback_data="swap")
    )

    bot.send_message(
        m.chat.id,
        f"👋 Welcome <b>{m.from_user.first_name}</b>\n\n"
        "🤖 <b>AI Photo Bot</b>\n\n"
        "🧼 Remove Background\n"
        "🔁 Face Swap\n\n"
        "👇 Choose option:",
        reply_markup=kb
    )

# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "bg":
        msg = bot.send_message(c.message.chat.id, "📸 Send image for <b>Background Remove</b>")
        bot.register_next_step_handler(msg, remove_bg)

    elif c.data == "swap":
        msg = bot.send_message(c.message.chat.id, "🧑 Send <b>FIRST image</b> (Base Face)")
        bot.register_next_step_handler(msg, swap_step1)

# ===== REMOVE BG =====
def remove_bg(m):
    if not m.photo:
        bot.send_message(m.chat.id, "❌ Please send an image")
        return

    file_info = bot.get_file(m.photo[-1].file_id)
    img = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    ).content

    r = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers={"X-Api-Key": REMOVE_BG_API_KEY},
        files={"image_file": img},
        data={"size": "auto"},
        timeout=60
    )

    if r.status_code == 200:
        bot.send_document(m.chat.id, r.content, caption="✅ Background Removed")
    else:
        bot.send_message(m.chat.id, "❌ Background remove failed")

# ===== FACE SWAP =====
def swap_step1(m):
    if not m.photo:
        bot.send_message(m.chat.id, "❌ Send an image")
        return

    file_info = bot.get_file(m.photo[-1].file_id)
    base = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    ).content

    msg = bot.send_message(m.chat.id, "😎 Send <b>SECOND image</b> (Face to swap)")
    bot.register_next_step_handler(msg, swap_step2, base)

def swap_step2(m, base_img):
    if not m.photo:
        bot.send_message(m.chat.id, "❌ Send an image")
        return

    file_info = bot.get_file(m.photo[-1].file_id)
    target = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    ).content

    url = "https://face-swap1.p.rapidapi.com/swap"

    r = requests.post(
        url,
        headers={
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "face-swap1.p.rapidapi.com"
        },
        files={
            "source": ("source.jpg", base_img),
            "target": ("target.jpg", target)
        },
        timeout=90
    )

    if r.status_code == 200:
        bot.send_document(m.chat.id, r.content, caption="✅ Face Swapped")
    else:
        bot.send_message(m.chat.id, "❌ Face swap failed")

# ===== RUN =====
bot.infinity_polling()
