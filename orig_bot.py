from pprint import pprint
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler

import bot_config

button_rest = 'Проверить номер телефона'


def button_rest_handler(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(
        text="Ответ",
        reply_markup=ReplyKeyboardRemove()
    )
    pprint(text)


def message_handler(update: Update, context: CallbackContext):
    """
        обработка текстовых сообщений
    update - событие которое пришло из API телеграмма
    context - пользовательский контекст
    """
    # определяем что нажата кнопка
    text = update.message.text
    if text == button_rest:
        return button_rest_handler(update=update, context=context)

    # добавляем клавиатуру
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button_rest)
            ],
        ],
        resize_keyboard=True
    )

    # ответ бота
    update.message.reply_text(
        text=f"Здравствуйте {update.message.from_user.first_name} для подтверения подписки укажите контактный телефон",
        reply_markup=reply_markup,
    )



def main():
    """ Основная функция (точкка входа) """
    updater = Updater(token=bot_config.TOKEN, use_context=True)

    # подключаем слушатель события отправки сообщения
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
