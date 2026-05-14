import telebot
import requests
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8631411157:AAG6RC7EMYvgp6mvcIb0fNvL4xOINdVTcWc'
CHANNEL_1 = '@CODEX_HABESHA'
CHANNEL_2 = '@officialcoders'
API_URL = "https://viscodev.x10.mx/Flux-MAX/api.php"

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def is_subscribed(user_id):
    try:
        status1 = bot.get_chat_member(CHANNEL_1, user_id).status
        status2 = bot.get_chat_member(CHANNEL_2, user_id).status
        active_status = ['member', 'administrator', 'creator']
        return status1 in active_status and status2 in active_status
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            f"Welcome back, **{user_name}**! ✨\n\n"
            "Send me a prompt to generate your masterpiece.",
            parse_mode="Markdown"
        )
    else:
        welcome_text = (
            f"Hello **{user_name}**,\n\n"
            "To unlock the Premium Image Generation features, please join our updates channels below."
        )
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates 1", url=f"https://t.me/{CHANNEL_1.replace('@', '')}"))
        markup.row(types.InlineKeyboardButton("✨ Join Updates 2", url=f"https://t.me/{CHANNEL_2.replace('@', '')}"))
        markup.row(types.InlineKeyboardButton("✅ Verify Membership", callback_data="check_sub"))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "✅ **Verification successful!**\n\nNow, tell me what you want to create today.",
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Please join both channels to continue.", show_alert=True)

@bot.message_handler(func=lambda message: True)
def generate_image(message):
    if not is_subscribed(message.from_user.id):
        start(message)
        return

    prompt = message.text
    loading_msg = bot.reply_to(message, "Generating... 🎨", parse_mode="Markdown")
    
    try:
        params = {"prompt": prompt, "aspect_ratio": "1:1"}
        response = requests.get(API_URL, params=params, timeout=120)
        data = response.json()

        if data.get("success"):
            image_url = data['image_url']
            caption = (
                f"✨ **Creation Complete**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 `{prompt}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Created via @{bot.get_me().username}"
            )
            bot.send_photo(message.chat.id, image_url, caption=caption, parse_mode="Markdown")
            bot.delete_message(message.chat.id, loading_msg.message_id)
        else:
            bot.edit_message_text("❌ Failed to generate. Please try a different prompt.", message.chat.id, loading_msg.message_id)
    except Exception as e:
        try:
            bot.edit_message_text("⚠️ Connection error. Try again.", message.chat.id, loading_msg.message_id)
        except:
            pass

if __name__ == "__main__":
    print("🚀 Pro Bot is starting...")
    keep_alive()
    bot.infinity_polling()
