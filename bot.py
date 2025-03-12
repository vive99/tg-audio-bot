from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InputMediaPhoto, InputMediaAudio, ReplyKeyboardMarkup, KeyboardButton
import asyncio

API_TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'
CHANNEL_ID = '@mus_eq'  # ID твоего канала

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временные хранилища
user_images = {}
user_audios = {}

# Кнопка "Пропустить"
skip_kb = ReplyKeyboardMarkup(resize_keyboard=True)
skip_kb.add(KeyboardButton("🔽 Пропустить"))

# Шаг 1. Получаем картинку
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_images[message.from_user.id] = file_id
    await message.reply("Картинка получена ✅ Теперь отправь аудиофайл 🎵.")

# Шаг 2. Получаем аудио
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_images:
        await message.reply("❗ Сначала отправь картинку, чтобы использовать её в посте.")
        return

    user_audios[user_id] = message.audio
    await message.reply("Хочешь добавить описание под постом? ✍️\n"
                        "Напиши текст или нажми 'Пропустить'.", reply_markup=skip_kb)

# Шаг 3. Получаем описание или пропуск
@dp.message_handler(lambda message: message.text or message.text == "🔽 Пропустить")
async def handle_caption(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_audios or user_id not in user_images:
        await message.reply("❗ Ты еще не отправил полный комплект (картинка + аудио).")
        return

    audio = user_audios[user_id]
    photo_id = user_images[user_id]

    # Если пропустил — не добавляем описание
    final_caption = "" if message.text == "🔽 Пропустить" else message.text

    # Готовим media_group
    media = [
        InputMediaPhoto(media=photo_id),  # Фото без подписи
        InputMediaAudio(
            media=audio.file_id,
            caption=final_caption  # Описание идет к аудио (в рамках альбома)
        )
    ]

    # Отправляем в канал
    await bot.send_media_group(CHANNEL_ID, media)

    await message.reply("Пост с картинкой и треком опубликован! ✅", reply_markup=types.ReplyKeyboardRemove())

    # Чистим данные
    del user_images[user_id]
    del user_audios[user_id]

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
