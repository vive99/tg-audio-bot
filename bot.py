import os
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = os.getenv("API_TOKEN")  # Из переменных окружения
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Из переменных окружения

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище для картинок и аудио
user_data = {}

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_data[message.from_user.id] = {'photo': file_id}
    await message.reply("Картинка получена. Теперь отправь аудиофайл.")

@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    file_id_audio = message.audio.file_id

    if user_id in user_data and 'photo' in user_data[user_id]:
        user_data[user_id]['audio'] = file_id_audio
        user_data[user_id]['file_name'] = message.audio.file_name

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Пропустить", "Скопировать название аудио файла в описание поста")
        await message.reply("Хочешь добавить описание?", reply_markup=keyboard)
    else:
        await message.reply("Сначала отправь картинку!")

@dp.message_handler(lambda message: message.text in ["Пропустить", "Скопировать название аудио файла в описание поста"])
async def handle_description_choice(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id)

    if not data:
        await message.reply("Сначала отправь картинку и аудиофайл.")
        return

    if message.text == "Скопировать название аудио файла в описание поста":
        description = data['file_name']
        await post_to_channel(data['photo'], data['audio'], description)
    else:
        await post_to_channel(data['photo'], data['audio'], "")

    await message.reply("Пост опубликован!", reply_markup=types.ReplyKeyboardRemove())
    del user_data[user_id]

@dp.message_handler()
async def handle_custom_description(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id)

    if data:
        await post_to_channel(data['photo'], data['audio'], message.text)
        await message.reply("Пост опубликован с описанием!", reply_markup=types.ReplyKeyboardRemove())
        del user_data[user_id]
    else:
        await message.reply("Сначала отправь картинку и аудио!")

async def post_to_channel(photo_id, audio_id, caption):
    await bot.send_photo(CHANNEL_ID, photo_id, caption=caption)
    await bot.send_audio(CHANNEL_ID, audio_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
