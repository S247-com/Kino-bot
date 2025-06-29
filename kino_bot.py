# kino_bot.py

import telebot
import json
import os
from config import *

bot = telebot.TeleBot(TOKEN)

# 📁 JSON fayllarni yuklash va saqlash funksiyalari
def load_json(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default_data, f)
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

kino_baza = load_json(BAZA_FILE, {})
stat = load_json(STAT_FILE, {})
users = load_json("users.json", [])

# ✅ Ommaviy kanalga obuna tekshiruvi
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# 🔐 Shaxsiy kanalga a'zolik tekshiruvi
def check_private_access(user_id):
    try:
        member = bot.get_chat_member(PRIVATE_CHANNEL, user_id)
        return member.status != 'left'
    except:
        return False

# 🚀 /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    text = (
        "👋 Salom!\n\n"
        "🎥 Kinoni olish uchun quyidagilarni bajaring:\n"
        f"1. 📢 Ommaviy kanalga obuna bo‘ling: {PUBLIC_CHANNEL}\n"
        f"2. 🔐 Shaxsiy kanalga so‘rov yuboring: {CHECK_URL}\n\n"
        "✅ Hammasi bajarilgach, kino kodini yuboring."
    )
    bot.send_message(user_id, text)

# 🛠 /panel — admin uchun statistika
@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    # 📊 Statistika matni
    text = "📊 Statistika:\n\n"
    text += f"👥 Botda {len(users)} ta foydalanuvchi bor.\n"

    if stat:
        top_kod = max(stat, key=stat.get)
        text += f"🔥 Eng ko‘p so‘ralgan kod: {top_kod} ({stat[top_kod]} marta)\n"
    else:
        text += "📭 Hozircha hech qanday so‘rov yo‘q.\n"

    text += (
        "\n➕ Yangi kino qo‘shish: /add KOD FILE_ID\n"
        "🗑 Kodni o‘chirish: /del KOD\n"
        "📄 Kodlar ro‘yxati: /list"
    )

    bot.send_message(ADMIN_ID, text)

# ➕ /add — yangi kod qo‘shish
@bot.message_handler(commands=['add'])
def add_kino(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, kod, file_id = message.text.split(maxsplit=2)
        kino_baza[kod] = file_id
        save_json(BAZA_FILE, kino_baza)
        bot.reply_to(message, f"✅ Kod '{kod}' muvaffaqiyatli qo‘shildi.")
    except:
        bot.reply_to(message, "❌ Format xato. To‘g‘ri format: /add KOD FILE_ID")

# 🗑 /del — kod o‘chirish
@bot.message_handler(commands=['del'])
def del_kino(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, kod = message.text.split()
        if kod in kino_baza:
            del kino_baza[kod]
            save_json(BAZA_FILE, kino_baza)
            bot.reply_to(message, f"🗑 Kod '{kod}' o‘chirildi.")
        else:
            bot.reply_to(message, "❌ Bunday kod topilmadi.")
    except:
        bot.reply_to(message, "❌ Format xato. To‘g‘ri format: /del KOD")

# 📃 /list — barcha kodlar ro‘yxati
@bot.message_handler(commands=['list'])
def list_kodlar(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not kino_baza:
        bot.send_message(ADMIN_ID, "📭 Hech qanday kod mavjud emas.")
        return
    text = "📄 Mavjud kodlar:\n"
    for kod in kino_baza:
        text += f"▫️ {kod}\n"
    bot.send_message(ADMIN_ID, text)

# 📽 Video yuborilganda file_id chiqarish
@bot.message_handler(content_types=['video'])
def get_file_id(message):
    if message.from_user.id == ADMIN_ID:
        file_id = message.video.file_id
        bot.reply_to(message, f"🎬 VIDEO FILE_ID:\n{file_id}")

# 💬 Kino kodi yuborilganida ishlaydi
@bot.message_handler(func=lambda m: True)
def get_kod(message):
    user_id = message.from_user.id
    kod = message.text.strip()

    # ✅ Foydalanuvchini ro‘yxatga olish
    if user_id not in users:
        users.append(user_id)
        save_json("users.json", users)

    # ❌ Obuna tekshiruv
    if not is_subscribed(user_id):
        return bot.reply_to(message, f"📛 Avval ommaviy kanalga obuna bo‘ling: {PUBLIC_CHANNEL}")
    if not check_private_access(user_id):
        return bot.reply_to(message, f"🔐 Avval shaxsiy kanalga so‘rov yuboring: {CHECK_URL}")

    # 🎬 Kodni tekshirish
    if kod in kino_baza:
        file_id = kino_baza[kod]
        stat[kod] = stat.get(kod, 0) + 1
        save_json(STAT_FILE, stat)
        bot.send_video(user_id, file_id, caption="🎬 Mana siz so‘ragan kino.")
    else:
        bot.send_message(user_id, "❌ Bunday kod topilmadi.")

# ▶️ Botni ishga tushirish
print("✅ Bot ishga tushdi...")
bot.polling()