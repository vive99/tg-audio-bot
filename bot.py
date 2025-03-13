from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import os
import json
import asyncio

API_TOKEN = os.getenv('7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY')
CHANNEL_ID = '@mus_eq'

app = Flask(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def get_description_keyboard(file_name):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Скопировать название в описание", callback_data=f"copy_{file_name}"))
    return keyboard

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
        new_caption = f"{file_name} - {original_file_name}"

        await bot.send_media_group(
            CHANNEL_ID,
            [
                InputMediaPhoto(media=user_data[user_id]['photo']),
                types.InputMediaAudio(media=file_id_audio, caption=new_caption)
            ]
        )

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

        await bot.send_media_group(
            CHANNEL_ID,
            [
                InputMediaPhoto(media=user_data[user_id]['photo']),
                types.InputMediaAudio(media=file_id_audio, caption=caption)
            ]
        )

        del user_data[user_id]
        await message.reply(f"Публикация успешна с описанием: {caption}")
    else:
        await message.reply("Ошибка! Для публикации нужны и картинка, и аудио.")

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = types.Update(**json.loads(json_str))
    dp.process_update(update)
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Используем asyncio для запуска бота
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    app.run(host='0.0.0.0', port=5000)
