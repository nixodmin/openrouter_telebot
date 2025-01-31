Пример кода на Python для подключения к Телеграм боту нейросетевой модели ( использован API от openrouter.ai ).

1. Создайте в Telegram бота через BotFather и получите Токен вашего бота.
2. Создайте учётку в openrouter.ai и создайте API ключ
3. На Windows или Linux установите и обновите Python (у меня всё работает на версии 3.12.3)
4. Через pip установите все требуемые зависимости
5. Запустите файл tbot.py в консоли или в вашей IDE

Для Windows не требуется создавать отдельного виртуального окружения для пользователя,
поэтому текст ниже для пользователей Debian-based линукс

Для примера в качестве пользователя испольую user, обязательно замените на свой вариант

В каталоге /home/user должен лежать файл tbot.py (содержимое ниже, либо скачайте файл с этого гита https://github.com/nixodmin/openrouter_telebot/blob/main/tbot.py )

Создаём из-под вашего пользователя виртуальное окружение для питона:
```
sudo apt install python3.12-venv
python3 -m venv my-venv
```
Устанавливаем требуемые библиотеки в виртуальное окружение
```
my-venv/bin/pip install python-telegram-bot 
my-venv/bin/pip install aiohttp
```
Проверьте, что всё работает, запустите скрипт в консоли и обменяйтесь сообщениями с ботом в Телеграм:
```
my-venv/bin/python3 tbot.py
```
Если всё работает (учтите, что бесплатная модель может быть перегружена запросами), то сделайте из скрипта сервис:
```
sudo nano /etc/systemd/system/tbot.service
```
Содержимое файла tbot.service:
```
[Unit]
Description=Tbot Python Script Service
After=network.target

[Service]
ExecStart=/home/user/my-venv/bin/python3 /home/user/tbot.py
WorkingDirectory=/home/user
Restart=always
User=user
Group=user

[Install]
WantedBy=multi-user.target
```
После создания файла tbot.service нужно обновить systemd
```
sudo systemctl daemon-reload
```
Запускаем сервис с помощью команды
```
sudo systemctl start tbot.service
```
Смотрим, что он запустился и работает
```
sudo systemctl status tbot.service
```
Чтобы включить его в автоматический запуск после перезагрузки системы
```
sudo systemctl enable tbot.service
```
Перезапуск сервиса
```
sudo systemctl restart tbot.service
```
Остановка сервиса
```
sudo systemctl stop tbot.service
```

Сам скрипт

```
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import asyncio
import json
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)  # Создание логгера

TOKEN = 'ТОКЕН_ВАШЕГО_БОТА' # Токен бота
API_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions' # URL для работы с API openrouter.ai
API_KEY = 'API_КЛЮЧ'  # Ваш API ключ, который вы создали на openrouter.ai
MODEL = 'deepseek/deepseek-r1:free'  # Модель, которую вы хотите использовать (по умолчанию бесплатная, но перегруженная запросами)

# проверка, что сам скрипт работает производится командой "/status"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Скрипт чат бота активен.")

# обработка сообщений в чатах, где подключен бот
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_input = update.message.text

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

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_ENDPOINT, json=api_data, headers=headers, timeout=10) as response:
                response.raise_for_status()
                api_response = await response.json()

                # Логирование ответа API
                logger.info(f"API Response: {api_response}")

                # Проверка наличия данных в ответе
                if "choices" in api_response and len(api_response["choices"]) > 0:
                    try:
                        assistant_response = api_response["choices"][0]["message"]["content"]
                        if assistant_response.strip():  # Проверка на пустой текст
                            await update.message.reply_text(assistant_response)
                        else:
                            await update.message.reply_text("API вернул пустой ответ.")
                    except KeyError:
                        await update.message.reply_text("Ошибка API: неверная структура ответа.")
                else:
                    await update.message.reply_text("Ошибка API: ответ не содержит данных.")

    except asyncio.TimeoutError:
        await update.message.reply_text("API не отвечает более 10 секунд")
    except aiohttp.ClientError as e:
        await update.message.reply_text(f"Ошибка API: {e}")
def main() -> None:
    # Создаем экземпляр ApplicationBuilder и передаем ему токен бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("status", start))

    # Регистрируем обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем обработку сообщений
    application.run_polling()

if __name__ == "__main__":
    main()
```
