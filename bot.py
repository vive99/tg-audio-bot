from flask import Flask
import threading
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'  # Твой API токен
CHANNEL_ID = '@Mus.eQ 🎵'  # Твой канал

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Запуск Flask сервера в отдельном потоке
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Обработчик фото
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_images[message.from_user.id] = file_id
    await message.reply("Картинка получена. Теперь отправь аудиофайл.")

# Обработчик аудио
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    file_id_audio = message.audio.file_id
    audio_title = message.audio.title
    caption = message.caption if message.caption else ""

    # Предложим пользователю добавить описание
    await message.reply("Хотите добавить описание к посту?", reply_markup=keyboard)

    # Сохраняем аудио и его название для дальнейшего использования
    user_images[user_id] = {
        'audio_file_id': file_id_audio,
        'audio_title': audio_title,
        'caption': caption
    }

# Обработчик ответа на кнопку
@dp.message_handler(lambda message: message.text in ["Пропустить", "Скопировать название аудио в описание поста"])
async def handle_description(message: types.Message):
    user_id = message.from_user.id
    user_data = user_images.get(user_id)

    if not user_data:
        await message.reply("Сначала отправьте аудиофайл и картинку.")
        return

    if message.text == "Пропустить":
        caption = user_data['caption']
    elif message.text == "Скопировать название аудио в описание поста":
        caption = user_data['audio_title']

    file_id_audio = user_data['audio_file_id']

    # Публикуем аудио с описанием (вместо просто аудио - с картинкой + описание)
    if user_data.get('image_file_id'):
        file_id_image = user_data['image_file_id']
        media = [
            types.InputMediaPhoto(media=file_id_image),
            types.InputMediaAudio(media=file_id_audio, caption=caption)
        ]
        await bot.send_media_group(CHANNEL_ID, media)
    else:
        await bot.send_audio(CHANNEL_ID, file_id_audio, caption=caption)
    
    await message.reply("Пост опубликован!")
    del user_images[user_id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
