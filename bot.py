from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import exceptions
import logging
import os

# Логи
logging.basicConfig(level=logging.INFO)

# Загрузка переменных
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище
user_data = {}

# Старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Пришли картинку, чтобы начать создание поста.")

# Получаем картинку
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_data[message.from_user.id] = {'photo': file_id}
    await message.reply("Картинка получена! Теперь пришли аудиофайл.")

# Получаем аудио
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    audio_id = message.audio.file_id
    title = message.audio.title or "Без названия"
    
    if user_id not in user_data or 'photo' not in user_data[user_id]:
        await message.reply("Сначала пришли картинку!")
        return
    
    user_data[user_id]['audio'] = audio_id
    user_data[user_id]['audio_title'] = title
    
    # Кнопки для выбора
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Пропустить"))
    keyboard.add(KeyboardButton("Скопировать название аудио файла в описание поста"))
    
    await message.reply("Хочешь добавить описание? Отправь его или выбери кнопку ниже:", reply_markup=keyboard)

# Обработка описания или кнопок
@dp.message_handler(lambda message: True, content_types=types.ContentType.TEXT)
async def handle_caption(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or 'audio' not in user_data[user_id] or 'photo' not in user_data[user_id]:
        await message.reply("Начни с отправки картинки и аудио.")
        return

    # Если выбрали "Скопировать название аудио файла"
    if message.text == "Скопировать название аудио файла в описание поста":
        caption = user_data[user_id].get('audio_title', '')
    elif message.text == "Пропустить":
        caption = ''
    else:
        caption = message.text

    # Готовим альбом
    media = [
        types.InputMediaPhoto(media=user_data[user_id]['photo'], caption=caption),
        types.InputMediaAudio(media=user_data[user_id]['audio'])
    ]

    try:
        await bot.send_media_group(CHANNEL_ID, media)
        await message.reply("Пост успешно опубликован! ✅", reply_markup=types.ReplyKeyboardRemove())
    except exceptions.TelegramAPIError as e:
        await message.reply(f"Ошибка публикации: {e}")
    finally:
        user_data.pop(user_id, None)

# Глобальный обработчик ошибок
@dp.errors_handler()
async def global_error_handler(update, error):
    if isinstance(error, exceptions.TelegramAPIError):
        await update.message.reply(f"Ошибка Telegram API: {error}")
    else:
        await update.message.reply(f"Произошла ошибка: {error}")
    return True

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
