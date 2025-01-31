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
