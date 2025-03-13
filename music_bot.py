import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import os

TOKEN = '7963741763:AAG5cCO-gLJbWOhfOMTR-nNA_kKkVrMWqSY'
CHANNEL_ID = '@mus_eq'

user_data = {}

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Давайте создадим пост с музыкой.")
    user_data[update.effective_chat.id] = {}
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отправьте картинку.")

def image(update, context):
    user_data[update.effective_chat.id]['image'] = update.message.photo[-1].file_id
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отправьте аудиофайл.")

def audio(update, context):
    user_data[update.effective_chat.id]['audio'] = update.message.audio.file_id
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отправьте описание или напишите 'название', чтобы использовать название аудио.")

def caption(update, context):
    if update.message.text.lower() == 'название':
        user_data[update.effective_chat.id]['caption'] = update.message.audio.title if update.message.audio.title else "Без названия"
    else:
        user_data[update.effective_chat.id]['caption'] = update.message.text
    send_post(update, context)

def send_post(update, context):
    data = user_data.get(update.effective_chat.id)
    if data and 'image' in data and 'audio' in data and 'caption' in data:
        try:
            context.bot.send_photo(chat_id=CHANNEL_ID, photo=data['image'], caption=data['caption'])
            context.bot.send_audio(chat_id=CHANNEL_ID, audio=data['audio'])
            context.bot.send_message(chat_id=update.effective_chat.id, text="Пост опубликован!")
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка: {e}")
        finally:
            del user_data[update.effective_chat.id]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Не все данные получены. Пожалуйста, начните сначала с /start.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.PHOTO, image))
    dp.add_handler(MessageHandler(filters.AUDIO, audio))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, caption))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
