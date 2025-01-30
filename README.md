Пример кода на Python для подключения к Телеграм боту нейросетевой модели ( использован API от openrouter.ai ).

1. Создайте в Telegram бота через BotFather и получите Токен вашего бота.
2. Создайте учётку в openrouter.ai и создайте API ключ
3. На Windows, Linux или MacOS установите Python
4. Через pip установите все требуемые зависимости ( pip install telebot requests json )
5. Запустите файл ( python openrouter_telebot.py )

```
import telebot
import requests
import json
from telebot import types

TOKEN = 'ВАШ_ТОКЕН_ОТ_БОТА_TELEGRAM'
API_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'
API_KEY = 'ВАШ_API_КЛЮЧ_НА_openrouter.ai'  # Ваш API ключ, сгенерированный на openrouter.ai
MODEL = 'deepseek/deepseek-r1:free'  # Модель, которую вы хотите использовать (по умолчанию - бесплатная, но с задержками)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вас приветствует нейросетевой чат бот!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text

    # Подготовка данных для API запроса
    api_data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Use russian language, be friendly, be short"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False
    }

    # Заголовки для запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Отправляем запрос API
    response = requests.post(API_ENDPOINT, json=api_data, headers=headers)

    if response.status_code == 200:
        # Парсим ответ API
        api_response = json.loads(response.text)

        if "choices" in api_response and len(api_response["choices"]) > 0:
            # Получаем текст от нейросети из ответа API
            assistant_response = api_response["choices"][0]["message"]["content"]
            # Отправляем текст пользователю
            bot.reply_to(message, assistant_response)
    else:
        bot.reply_to(message, "Ошибка API")

if __name__ == "__main__":
    bot.polling(none_stop=True)
```
