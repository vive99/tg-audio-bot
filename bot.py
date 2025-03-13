import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto
from aiogram.utils import executor

# Получаем переменные окружения
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище для картинок
user_images = {}

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_images[message.from_user.id] = file_id
    await message.reply("Картинка получена. Теперь отправь аудиофайл.")

@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    file_id_audio = message.audio.file_id
    caption = message.caption if message.caption else ""

    if user_id in user_images:
        file_id_image = user_images[user_id]
        media = [
            InputMediaPhoto(media=file_id_image),
            types.InputMediaAudio(media=file_id_audio, caption=caption)
        ]
        await bot.send_media_group(CHANNEL_ID, media)
        await message.reply("Пост опубликован!")
        del user_images[user_id]
    else:
        await bot.send_audio(CHANNEL_ID, file_id_audio, caption=caption)
        await message.reply("Аудио опубликовано без картинки. (Сначала пришли картинку!)")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
