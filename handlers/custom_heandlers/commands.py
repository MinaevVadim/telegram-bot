from database.date_base import *
from loader import bot
from telebot.types import Message
from states.find_hotels import *
from states.state_information import User
import datetime
from config_data import config
from keyboards.inline.inline_keyboards import *


@bot.message_handler(commands=['highprice', 'lowprice', 'bestdeal'])
def start_two(message: Message):
    User.dct[message.chat.id] = User()
    User.dct[message.chat.id].command = message.text
    User.dct[message.chat.id].date = datetime.datetime.now()
    bot.send_message(message.from_user.id, "Введите город, где будет проводиться поиск")
    bot.register_next_step_handler(message, get_city)


def get_city(message: Message):
    search_cities = SearchObject(search_city(message.text), config.search_location)
    bot.send_message(message.from_user.id, text='Уточните пожалуйста',
                     reply_markup=city_markup(city_founding(search_cities.request_to_api())))


def question_date(message: Message):
    User.dct[message.chat.id].check_in_out = message.text.split()
    if User.dct[message.chat.id].command == '/lowprice' \
            or User.dct[message.chat.id].command == '/highprice':
        bot.send_message(message.chat.id, 'Сколько отелей Вам вывести (Не больше 10)?')
        bot.register_next_step_handler(message, question_about_photo)
    else:
        bot.send_message(message.chat.id, 'Введите пожалуйста диапазон цен за отель через пробел (рубли)')
        bot.register_next_step_handler(message, price_range)


def price_range(message: Message):
    User.dct[message.chat.id].price = message.text.split()
    bot.send_message(message.from_user.id, "Введите пожалуйста диапазон расстояния от отеля"
                                           " до центра через пробел (км)")
    bot.register_next_step_handler(message, distance_center)


def distance_center(message: Message):
    User.dct[message.chat.id].distance = message.text.split()
    bot.send_message(message.from_user.id, 'Сколько отелей Вам вывести (Не больше 10)?')
    bot.register_next_step_handler(message, question_about_photo)


def question_about_photo(message: Message):
    User.dct[message.chat.id].count_hotels = int(message.text)
    text = 'Необходимость загрузки и вывода фотографий для каждого отеля ("Да/Нет")'
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboards())


def ready_photo(message: Message):
    User.dct[message.chat.id].count_photos = int(message.text)
    search_hotels = SearchObject(search_hotel(User.dct[message.chat.id].call_data), config.search_list)
    if User.dct[message.chat.id].command == '/lowprice':
        # text_hotels = ''
        for with_photo1 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                       User.dct[message.chat.id].check_in_out,
                                                                       User.dct[message.chat.id].count_hotels,
                                                                       User.dct[message.chat.id].count_photos)):
            # text_hotels += with_photo1[0]
            bot.send_media_group(message.chat.id, with_photo1[0])
            # if with_photo1[1] == 0:
            #     User.dct[message.chat.id].text_hotels = text_hotels
            #     base_date_orm(User.dct[message.chat.id].command,
            #                   User.dct[message.chat.id].date,
            #                   User.dct[message.chat.id].text_hotels)
    elif User.dct[message.chat.id].command == '/highprice':
        # text_hotels = ''
        for with_photo1 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                       User.dct[message.chat.id].check_in_out,
                                                                       User.dct[message.chat.id].count_hotels,
                                                                       User.dct[message.chat.id].count_photos,
                                                                       sort_price=False)):
            # text_hotels += with_photo1[0]
            bot.send_media_group(message.chat.id, with_photo1[0])
            # if with_photo1[1] == 0:
            #     User.dct[message.chat.id].text_hotels = text_hotels
            #     base_date_orm(User.dct[message.chat.id].command,
            #                   User.dct[message.chat.id].date,
            #                   User.dct[message.chat.id].text_hotels)
    else:
        # text_hotels = ''
        for with_photo2 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                       User.dct[message.chat.id].check_in_out,
                                                                       User.dct[message.chat.id].count_hotels,
                                                                       User.dct[message.chat.id].count_photos,
                                                                       User.dct[message.chat.id].price,
                                                                       User.dct[message.chat.id].distance)):
            # text_hotels += with_photo2[0]
            bot.send_media_group(message.chat.id, with_photo2[0])
            # if with_photo2[1] == 0:
            #     User.dct[message.chat.id].text_hotels = text_hotels
            #     base_date_orm(User.dct[message.chat.id].command,
            #                   User.dct[message.chat.id].date,
            #                   User.dct[message.chat.id].text_hotels)


@bot.callback_query_handler(func=lambda call: True)
def get_photo_two(call):
    bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за выбор!')
    if call.data == "Да":
        bot.send_message(call.message.chat.id, 'Сколько фото Вам вывести (Не больше 5)?')
        bot.register_next_step_handler(call.message, ready_photo)
    elif call.data == "Нет":
        search_hotels = SearchObject(search_hotel(User.dct[call.message.chat.id].call_data), config.search_list)
        if User.dct[call.message.chat.id].command == '/lowprice':
            text_hotels = ''
            for no_photo1 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                         User.dct[call.message.chat.id].check_in_out,
                                                                         User.dct[call.message.chat.id].count_hotels),
                                                       False):
                text_hotels += no_photo1[0]
                bot.send_message(call.message.chat.id, no_photo1[0])
                if no_photo1[1] == 0:
                    User.dct[call.message.chat.id].text_hotels = text_hotels
                    base_date_orm(User.dct[call.message.chat.id].command,
                                  User.dct[call.message.chat.id].date,
                                  User.dct[call.message.chat.id].text_hotels)
        elif User.dct[call.message.chat.id].command == '/highprice':
            text_hotels = ''
            for no_photo1 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                         User.dct[call.message.chat.id].check_in_out,
                                                                         User.dct[call.message.chat.id].count_hotels,
                                                                         sort_price=False), False):
                text_hotels += no_photo1[0]
                bot.send_message(call.message.chat.id, no_photo1[0])
                if no_photo1[1] == 0:
                    User.dct[call.message.chat.id].text_hotels = text_hotels
                    base_date_orm(User.dct[call.message.chat.id].command,
                                  User.dct[call.message.chat.id].date,
                                  User.dct[call.message.chat.id].text_hotels)
        else:
            text_hotels = ''
            for no_photo2 in text_transformation_photo(property_founding(search_hotels.request_to_api(),
                                                                         User.dct[call.message.chat.id].check_in_out,
                                                                         User.dct[call.message.chat.id].count_hotels,
                                                                         price_r=User.dct[call.message.chat.id].price,
                                                                         distance_c=User.dct[
                                                                             call.message.chat.id].distance),
                                                       False):
                text_hotels += no_photo2[0]
                bot.send_message(call.message.chat.id, no_photo2[0])
                if no_photo2[1] == 0:
                    User.dct[call.message.chat.id].text_hotels = text_hotels
                    base_date_orm(User.dct[call.message.chat.id].command,
                                  User.dct[call.message.chat.id].date,
                                  User.dct[call.message.chat.id].text_hotels)
    elif call.data.isdigit():
        User.dct[call.message.chat.id].call_data = call.data
        bot.send_message(call.message.chat.id, 'Введите пожалуйста, с какого по какое число считать стоимость'
                                               ' гостиницы по форме: ГГГГ-ММ-ДД ГГГГ-ММ-ДД')
        bot.register_next_step_handler(call.message, question_date)
