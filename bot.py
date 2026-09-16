import os
import telebot
from openai import OpenAI

# Данные берутся из настроек сервера безопасности
T_KEY = os.getenv("7943185727:AAFDwCm86HgST9QpZRG5r9_lGNVMIoVE3WQ")
O_KEY = os.getenv("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")

bot = telebot.TeleBot(T_KEY)
ai_client = OpenAI(
    base_url="https://openrouter.ai",
    api_key=O_KEY,
)

sessions = {}

@bot.message_handler(commands=['start', 'clear'])
def send_welcome(message):
    sessions[message.chat.id] = []
    bot.reply_to(message, "Привет! Задавай вопросы, я помню наш диалог. Сбросить контекст: /clear.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text

    if user_id not in sessions:
        sessions[user_id] = []

    sessions[user_id].append({"role": "user", "content": text})

    if len(sessions[user_id]) > 10:
        sessions[user_id] = sessions[user_id][-10:]

    try:
        response = ai_client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=sessions[user_id]
        )
        ai_text = response.choices.message.content
        sessions[user_id].append({"role": "assistant", "content": ai_text})
        bot.reply_to(message, ai_text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
