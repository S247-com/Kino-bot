from telebot import TeleBot
from telebot.types import Message
from config import JOIN_CHANNELS, BOT_TOKEN

bot = TeleBot(BOT_TOKEN)

def check_user_subscribed(user_id):
    for channel in JOIN_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["member", "administrator", "creator"]:
                continue  # Obuna bo‘lgan, keyingisiga o‘tamiz
            else:
                return False  # Bunday statusda emas
        except Exception as e:
            print(f"Xatolik: {e}")
            return False  # Kanalni topa olmadi yoki xato
    return True  # Hammasiga obuna bo‘lgan