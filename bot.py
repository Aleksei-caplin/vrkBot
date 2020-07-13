from pprint import pprint
from urllib import parse
from urllib.request import Request, urlopen


import requests
from requests import HTTPError
from telegram import Bot, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler, CommandHandler, ConversationHandler

import bot_config

button_subscription = "Активировать подписку"
button_cancel = "Выйти из диалога"
button_ok = "Ok"

PHONE, FINISH = range(2)


def default_handler(update: Update, context: CallbackContext):
    """ Встречаем пользователя и предлогаем начать диалог командой /start """
    pprint("default")
    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text='Нажмите /start для заполнения анкеты!'
        #reply_markup=ReplyKeyboardRemove()
    )

    return PHONE


def start_handler(update: Update, context: CallbackContext):
    """ Активация бота при вводе команды /start """
    pprint("start")

    # добавляем клавиатуру под поле ввода
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить номер телефона", request_contact=True),
                KeyboardButton(text=button_cancel)
            ],
        ],
        resize_keyboard=True
    )

    # добавляем клавиатуру под сообщение
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_subscription, callback_data="subscribe", request_contact=True),
            ],
            [
                InlineKeyboardButton(text=button_cancel, callback_data="cancel"),
            ]
        ],
    )

    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=f"Здравствуйте {update.message.from_user.first_name} для подтверения подписки подтвердите контактный телефон",
        reply_markup=reply_markup
    )

    return PHONE


def phone_handler(update: Update, context: CallbackContext):
    """ Отправка телефона пользователем """
    pprint("phone")
    # получаем ответ пользователя
    user_phone = update.message.contact.phone_number
    user_chat_id = update.message.contact.user_id

    # отправляем запрос на сервер
    try:
        response = requests.post(bot_config.URL, data={'phone': user_phone, 'chat_id': user_chat_id}).json()
        if response["status"] == 200:
            text_to_user = "Запрос на подписку прошел успешно"
        else:
            text_to_user = "Пользователя с таким телефоном не найдено. За дополнительной информацией, обратитесь к админу"
        pprint(response)
    except requests.exceptions.HTTPError as e:
        text_to_user = f"Запрос на подписку прошел не успешно. Возможные ошибки {e.strerror}"

    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=text_to_user,
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def finish_handler(update: Update, context: CallbackContext):
    """ сообытие после отправки контакта """
    context.user_data[PHONE] = update.message.text
    pprint("finish")
    pprint(context.user_data[PHONE])

    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text="Ваш контакт отправлен в базу и подписка активирована",
    )

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны """
    pprint("cancel")


def main():
    """ Основная функция (точкка входа) """
    updater = Updater(token=bot_config.TOKEN, use_context=True)

    # подключаем метод для диалогов и обработки команд
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_handler)
        ],
        states={
            PHONE: [
                MessageHandler(Filters.all, phone_handler, pass_user_data=True),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )

    updater.dispatcher.add_handler(conversation_handler)
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=default_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
