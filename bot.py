from aiogram import Bot, Dispatcher, types, executor

# ✅ Твои данные
API_TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'
CHANNEL_ID = '@Mus_eQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище
user_data = {}


# Шаг 1: Получаем картинку
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    user_data[message.from_user.id] = {"photo": file_id}
    await message.reply("Картинка получена ✅\nТеперь отправь аудиофайл.")


# Шаг 2: Получаем аудио
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_audio(message: types.Message):
    user_id = message.from_user.id
    audio_file = message.audio.file_id
    title = message.audio.title or "Без названия"
    performer = message.audio.performer or "Неизвестный исполнитель"

    if user_id in user_data and "photo" in user_data[user_id]:
        user_data[user_id]["audio"] = audio_file
        user_data[user_id]["title"] = title
        user_data[user_id]["performer"] = performer

        # Кнопки
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Пропустить", "Скопировать название аудио файла в описание поста")

        await message.reply("Хочешь добавить описание к посту?", reply_markup=keyboard)
    else:
        await message.reply("Сначала отправь картинку!")


# Шаг 3: Принимаем описание и публикуем пост
@dp.message_handler(lambda message: message.text)
async def handle_description(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_data and "audio" in user_data[user_id]:
        text = message.text
        audio_file = user_data[user_id]["audio"]
        photo_file = user_data[user_id]["photo"]

        # Обработка кнопок
        if text == "Пропустить":
            caption = ""
        elif text == "Скопировать название аудио файла в описание поста":
            caption = f"{user_data[user_id]['title']} - {user_data[user_id]['performer']}"
        else:
            caption = text

        # Публикуем альбом
        media = [
            types.InputMediaPhoto(media=photo_file, caption=caption),
            types.InputMediaAudio(media=audio_file)
        ]
        await bot.send_media_group(CHANNEL_ID, media)

        await message.reply("✅ Пост опубликован!", reply_markup=types.ReplyKeyboardRemove())

        # Очистка
        del user_data[user_id]
    else:
        await message.reply("Сначала отправь картинку и аудио.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
