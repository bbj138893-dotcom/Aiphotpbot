import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ====== CONFIG ======
BOT_TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"

REMOVE_BG_API_KEY = "PUT_REMOVE_BG_API_KEY_HERE"
RAPIDAPI_KEY = "PUT_RAPIDAPI_KEY_HERE"

bot = telebot.TeleBot(BOT_TOKEN)

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🧼 Remove Background", callback_data="bg"),
        InlineKeyboardButton("🔁 Face Swap", callback_data="swap")
    )

    bot.send_message(
        message.chat.id,
        f"👋 Welcome {message.from_user.first_name}\n\n"
        "🤖 *AI Photo Bot*\n\n"
        "🧼 Remove Background\n"
        "🔁 Face Swap\n\n"
        "👇 Choose option:",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ====== BUTTONS ======
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):
    if call.data == "bg":
        bot.send_message(call.message.chat.id, "📸 Send image for *Background Remove*", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, remove_bg)

    elif call.data == "swap":
        bot.send_message(call.message.chat.id, "🧑 Send *FIRST image* (Base Face)", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, face_swap_step1)

# ====== BACKGROUND REMOVE ======
def remove_bg(message):
    if not message.photo:
        bot.reply_to(message, "❌ Image bhejo")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}")

    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": file.content},
        data={"size": "auto"},
        headers={"X-Api-Key": REMOVE_BG_API_KEY},
    )

    if response.status_code == 200:
        bot.send_document(message.chat.id, response.content, caption="✅ Background Removed")
    else:
        bot.send_message(message.chat.id, "❌ Background remove failed")

# ====== FACE SWAP ======
def face_swap_step1(message):
    if not message.photo:
        bot.reply_to(message, "❌ Image bhejo")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    base_img = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}").content

    bot.send_message(message.chat.id, "😎 Ab *SECOND image* bhejo (Swap Face)", parse_mode="Markdown")
    bot.register_next_step_handler(message, face_swap_step2, base_img)

def face_swap_step2(message, base_img):
    if not message.photo:
        bot.reply_to(message, "❌ Image bhejo")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    swap_img = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}").content

    url = "https://face-swap1.p.rapidapi.com/swap"

    files = {
        "source": base_img,
        "target": swap_img
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "face-swap1.p.rapidapi.com"
    }

    r = requests.post(url, files=files, headers=headers)

    if r.status_code == 200:
        bot.send_document(message.chat.id, r.content, caption="✅ Face Swapped")
    else:
        bot.send_message(message.chat.id, "❌ Face swap failed")

# ====== RUN ======
bot.infinity_polling()
