import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from flask import Flask
import asyncio

# Устанавливаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем Flask приложение для прослушивания порта
app = Flask(__name__)

# Вставляю твой API Token и ID канала
API_TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'
CHANNEL_ID = '@Mus.eQ'

# Инициализируем бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище для картинок, аудио и состояния
user_data = {}

# Кнопки для ввода описания
def get_description_keyboard(file_name):
    keyboard = InlineKeyboardMarkup()
    # Кнопка для копирования названия аудиофайла в описание
    keyboard.add(InlineKeyboardButton(text="Скопировать название в описание", callback_data=f"copy_{file_name}"))
    return keyboard

# Flask маршрут для прослушивания порта
@app.route('/')
def webhook():
    return 'Bot is running!'

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Сначала отправь мне картинку.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_data[message.from_user.id] = {'photo': file_id}
    await message.reply("Картинка получена. Теперь отправь аудиофайл.")

@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    file_id_audio = message.audio.file_id
    file_name = message.audio.file_name
    caption = message.caption if message.caption else ""

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['audio'] = (file_id_audio, file_name, caption)

    if 'photo' in user_data[user_id]:
        # Отправляем клавиатуру для выбора описания
        keyboard = get_description_keyboard(file_name)
        await message.reply("Теперь выбери описание для аудиофайла или добавь его ниже.", reply_markup=keyboard)
    else:
        await message.reply("Аудиофайл получен, но сначала отправь картинку!")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('copy_'))
async def process_callback_copy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    file_name = callback_query.data.split('_')[1]

    if user_id in user_data and 'photo' in user_data[user_id] and 'audio' in user_data[user_id]:
        file_id_audio, original_file_name, caption = user_data[user_id]['audio']
        new_caption = f"{file_name} - {original_file_name}"  # Формируем новое описание

        # Отправляем сообщение с аудио и картинкой
        await bot.send_media_group(
            CHANNEL_ID,
            [
                InputMediaPhoto(media=user_data[user_id]['photo']),
                types.InputMediaAudio(media=file_id_audio, caption=new_caption)
            ]
        )

        # Очищаем временные данные
        del user_data[user_id]
        await callback_query.answer(f"Описание для {file_name} добавлено: {new_caption}")
    else:
        await callback_query.answer("Ошибка! Для публикации нужны и картинка, и аудио.")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_data and 'photo' in user_data[user_id] and 'audio' in user_data[user_id]:
        user_data[user_id]['audio'] = (user_data[user_id]['audio'][0], user_data[user_id]['audio'][1], message.text)
        file_id_audio, original_file_name, caption = user_data[user_id]['audio']

        # Публикуем пост с текстом, если все 3 части готовы
        await bot.send_media_group(
            CHANNEL_ID,
            [
                InputMediaPhoto(media=user_data[user_id]['photo']),
                types.InputMediaAudio(media=file_id_audio, caption=caption)
            ]
        )

        # Очищаем временные данные
        del user_data[user_id]
        await message.reply(f"Публикация успешна с описанием: {caption}")
    else:
        await message.reply("Ошибка! Для публикации нужны и картинка, и аудио.")

# Убираем ошибки если не передали порты
if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(executor.start_polling(dp, skip_updates=True))
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    except Exception as e:
        print(f"Error while starting bot: {e}")
