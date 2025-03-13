from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'
CHANNEL_ID = '@Mus.eQ 🎵'  # твой канал

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

    # Предложение пользователю изменить название
    await message.reply("Введите описание для аудиофайла или отправьте 'пропустить', чтобы использовать стандартное описание.")

    # Ждем описание или пропуск
    @dp.message_handler(lambda msg: msg.text.lower() != 'пропустить')
    async def rename_audio(msg: types.Message):
        new_caption = msg.text
        if user_id in user_images:
            file_id_image = user_images[user_id]
            media = [
                types.InputMediaPhoto(media=file_id_image),
                types.InputMediaAudio(media=file_id_audio, caption=new_caption)
            ]
            await bot.send_media_group(CHANNEL_ID, media)
            await msg.reply("Пост с изображением и аудио опубликован!")
            del user_images[user_id]
        else:
            await bot.send_audio(CHANNEL_ID, file_id_audio, caption=new_caption)
            await msg.reply("Аудио без картинки опубликовано!")
        # После публикации ждем следующий ввод
        del user_images[user_id]
        return await dp.message_handler()  # Отменяем текущий хендлер

    # Если "пропустить"
    @dp.message_handler(lambda msg: msg.text.lower() == 'пропустить')
    async def skip_caption(msg: types.Message):
        if user_id in user_images:
            file_id_image = user_images[user_id]
            media = [
                types.InputMediaPhoto(media=file_id_image),
                types.InputMediaAudio(media=file_id_audio)
            ]
            await bot.send_media_group(CHANNEL_ID, media)
            await msg.reply("Пост с изображением и аудио опубликован без изменения описания!")
            del user_images[user_id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
