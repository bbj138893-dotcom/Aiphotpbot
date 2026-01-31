import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ---------- MENUS ----------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🧠 AI Tools", callback_data="tools"),
        InlineKeyboardButton("👤 My Account", callback_data="account"),
        InlineKeyboardButton("🌐 Language", callback_data="lang"),
        InlineKeyboardButton("ℹ️ About Bot", callback_data="about"),
        InlineKeyboardButton("📢 More Bots", url="https://t.me/YourChannel")
    )
    return kb

def tools_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔁 Face Swap", callback_data="faceswap"),
        InlineKeyboardButton("🧼 Remove Background", callback_data="bgremove"),
        InlineKeyboardButton("✨ Enhance Photo", callback_data="enhance"),
        InlineKeyboardButton("👕 Cloth Changing", callback_data="cloth"),
        InlineKeyboardButton("🧽 Remove Watermark", callback_data="watermark"),
        InlineKeyboardButton("🔙 Back", callback_data="back")
    )
    return kb

# ---------- START ----------
@bot.message_handler(commands=["start"])
def start(msg):
    text = (
        f"👋 Hello <b>{msg.from_user.first_name}</b>!\n\n"
        "🚀 <b>Welcome to AI Photo Tools Bot</b>\n"
        "Transform your photos using powerful AI tools — fast & secure ✨\n\n"
        "👇 Choose an option below:"
    )
    bot.send_message(msg.chat.id, text, reply_markup=main_menu())

# ---------- CALLBACKS ----------
@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    cid = c.message.chat.id

    if c.data == "tools":
        bot.edit_message_text(
            "🧠 <b>AI Tools</b>\nSelect any tool below:",
            cid, c.message.message_id, reply_markup=tools_menu()
        )

    elif c.data == "about":
        bot.edit_message_text(
            "✨ <b>What can this bot do?</b>\n"
            "Enhance & edit photos using AI.\n\n"
            "✅ Enhance Photo (HD)\n"
            "✅ Remove Background\n"
            "✅ Face Swap\n"
            "✅ Cloth Changing (Safe)\n"
            "✅ Remove Watermark (Basic)\n\n"
            "🔐 Safe • 🚀 Fast • 📱 Easy",
            cid, c.message.message_id, reply_markup=main_menu()
        )

    elif c.data == "account":
        bot.edit_message_text(
            f"👤 <b>My Account</b>\n\n"
            f"🆔 ID: <code>{c.from_user.id}</code>\n"
            f"📅 Joined: Today\n"
            f"⭐ Plan: Free",
            cid, c.message.message_id, reply_markup=main_menu()
        )

    elif c.data == "lang":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇵🇰 Urdu", callback_data="lang_ur"),
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )
        bot.edit_message_text("🌐 <b>Select Language</b>", cid, c.message.message_id, reply_markup=kb)

    elif c.data == "back":
        bot.edit_message_text("🏠 <b>Main Menu</b>", cid, c.message.message_id, reply_markup=main_menu())

    # ---- TOOL FLOWS (PLACEHOLDERS) ----
    elif c.data in ["faceswap", "bgremove", "enhance", "cloth", "watermark"]:
        tool_map = {
            "faceswap": "🔁 <b>Face Swap</b>\nSend the base photo.",
            "bgremove": "🧼 <b>Remove Background</b>\nSend an image.",
            "enhance": "✨ <b>Enhance Photo</b>\nSend a photo to enhance.",
            "cloth": "👕 <b>Cloth Changing</b>\nSend a photo (safe styles).",
            "watermark": "🧽 <b>Remove Watermark</b>\nSend image (basic).",
        }
        bot.edit_message_text(tool_map[c.data], cid, c.message.message_id)

# ---------- PHOTO HANDLER (DEMO) ----------
@bot.message_handler(content_types=["photo"])
def on_photo(msg):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back"))
    bot.send_message(
        msg.chat.id,
        "⏳ <b>Processing...</b>\n(This is demo output)\n\n"
        "🎉 <b>Done!</b>\nAI result would appear here.",
        reply_markup=kb
    )

# ---------- RUN ----------
bot.infinity_polling()
