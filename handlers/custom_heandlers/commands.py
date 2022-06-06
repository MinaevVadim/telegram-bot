from database.date_base import dct_history, db, InfoHistory, date_base
from loader import bot
from telebot.types import Message
from rapid_api.find_hotels import *
from states.state_information import User
import datetime
from config_data import config
from keyboards.inline.inline_keyboards import *
from telegram_bot_calendar import DetailedTelegramCalendar


@bot.message_handler(commands=['highprice', 'lowprice', 'bestdeal'])
def start_command(message: Message) -> None:
    """
    Пользователь вводит соответствующую команду, после этого создается объект класса User, записываем в словарь
    команду и id чата. Затем открываем базу данных и заполням таблицу нужными данными для команды history
    """
    User.dct[message.chat.id] = User()
    User.dct[message.chat.id].command = message.text
    User.dct[message.chat.id].id = str(message.chat.id)
    with db:
        dct_history[message.chat.id] = InfoHistory.create(id_name=User.dct[message.chat.id].id,
                                                          command=message.text, date=datetime.datetime.now())
    bot.send_message(message.from_user.id, "Введите пожалуйста город где будет проводиться поиск")
    bot.register_next_step_handler(message, get_city)


def get_city(message: Message) -> None:
    """
    Здесь мы ожидаем от пользователя ввод нужного города, делаем запрос к API, если сообщение было корректное, то
    просим его уточтить местоположение отеля в городе с помощью онлайн кнопок, в противном случае
    просим ввести город повторно
    """
    search_cities = SearchObject(search_city(message.text), config.search_location)
    api = city_markup(city_founding(search_cities.request_to_api()))
    if api is None:
        bot.send_message(message.from_user.id, 'Не корректно введены данные,'
                                               ' ничего не удалось найти, попробуйте еще раз&#10071',
                         parse_mode='HTML')
        bot.register_next_step_handler(message, get_city)
    else:
        bot.send_message(message.from_user.id, text='Уточните пожалуйста', reply_markup=api)


def price_range(message: Message) -> None:
    """
    Тут ожидаем от пользователя желаемый диапазон цен за отель, делаем проверку на
    правильность ввода, обязательно через пробел и текст должен содержать только цифры, данные записываем в словарь
    """
    if all([i.isdigit() for i in message.text.split()]) and len(message.text.split()) == 2 \
            and int(message.text.split()[0]) < int(message.text.split()[1]):
        User.dct[message.chat.id].price = message.text.split()
        bot.send_message(message.from_user.id, "Введите пожалуйста желаемый диапазон расстояния от отеля"
                                               " до центра через пробел (км)")
        bot.register_next_step_handler(message, distance_center)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста введите только цифрами и через пробел,'
                                               ' попробуйте еще раз&#10071', parse_mode='HTML')
        bot.register_next_step_handler(message, price_range)


def distance_center(message: Message) -> None:
    """
    Тут ожидаем от пользователя желаемый диапазон расстояния от отеля до центра города, делаем проверку на
    правильность ввода, обязательно через пробел и текст должен содержать только цифры, так же записываем
    в словарь диапазон расстояния
    """
    try:
        float(message.text.split()[0]), float(message.text.split()[1])
        if message.text.split()[0] < message.text.split()[1]:
            User.dct[message.chat.id].distance = message.text.split()
            bot.send_message(message.from_user.id, 'Сколько отелей вывести (Не более 10)?')
            bot.register_next_step_handler(message, question_about_photo)
    except ValueError:
        bot.send_message(message.from_user.id, 'Пожалуйста введите только цифрами и через пробел,'
                                               ' попробуйте еще раз&#10071', parse_mode='HTML')
        bot.register_next_step_handler(message, distance_center)


def question_about_photo(message: Message) -> None:
    """
    Получаем от пользователя нужное количество отелей для поиска и записываем данные в словарь, обрабатываем
    на коректность данных, далее справшиваем в необходимости загрузки фотографий, предлагая ответ в ввиде онлайн кнопок
    """
    if all([i.isdigit() for i in message.text]):
        User.dct[message.chat.id].count_hotels = int(message.text)
        text = 'Нужно ли будет загрузить и вывести фотографии для каждого отеля (Да / Нет)?'
        bot.send_message(message.from_user.id, text=text, reply_markup=keyboard_for_id())
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста введите только цифрами, попробуйте еще раз&#10071',
                         parse_mode='HTML')
        bot.register_next_step_handler(message, question_about_photo)


def ready_photo(message: Message) -> None:
    """
    Тут получаем информацию о неоходимом количестве фотографий с проверкой на корректность и в зависимости
    от введенной команды пользователя выводим весь итоговый результат по поиску отелей с фотографиями и записываем
    в базу данных информацию по по каждому отелю для команды history
    """
    if all([i.isdigit() for i in message.text]):
        User.dct[message.chat.id].count_photos = int(message.text)
        bot.send_message(message.chat.id, 'Подождите пожалуйcта, идет обработка результата &#9203', parse_mode='HTML')
        search_hotels = SearchObject(search_hotel(User.dct[message.chat.id].call_data), config.search_list)
        if User.dct[message.chat.id].command == '/lowprice':
            text_hotels = ''
            for with_photo1 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                                     User.dct[message.chat.id].check_in,
                                                                     User.dct[message.chat.id].check_out,
                                                                     User.dct[message.chat.id].count_hotels,
                                                                     User.dct[message.chat.id].count_photos)):
                text_hotels += f'{with_photo1[2]}\n'
                if len(with_photo1) == 4:
                    bot.send_message(message.chat.id, with_photo1[0], parse_mode='HTML')
                else:
                    bot.send_media_group(message.chat.id, with_photo1[0])
                    date_base(with_photo1, message.chat.id, text_hotels, bot.send_message, message.chat.id)
        elif User.dct[message.chat.id].command == '/highprice':
            text_hotels = ''
            for with_photo2 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                                     User.dct[message.chat.id].check_in,
                                                                     User.dct[message.chat.id].check_out,
                                                                     User.dct[message.chat.id].count_hotels,
                                                                     User.dct[message.chat.id].count_photos,
                                                                     sort_price=False)):
                text_hotels += f'{with_photo2[2]}\n'
                if len(with_photo2) == 4:
                    bot.send_message(message.chat.id, with_photo2[0], parse_mode='HTML')
                else:
                    bot.send_media_group(message.chat.id, with_photo2[0])
                    date_base(with_photo2, message.chat.id, text_hotels, bot.send_message, message.chat.id)
        else:
            text_hotels = ''
            for with_photo3 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                                     User.dct[message.chat.id].check_in,
                                                                     User.dct[message.chat.id].check_out,
                                                                     User.dct[message.chat.id].count_hotels,
                                                                     User.dct[message.chat.id].count_photos,
                                                                     User.dct[message.chat.id].price,
                                                                     User.dct[message.chat.id].distance)):
                text_hotels += f'{with_photo3[2]}\n'
                if len(with_photo3) == 4:
                    bot.send_message(message.chat.id, with_photo3[0], parse_mode='HTML')
                else:
                    bot.send_media_group(message.chat.id, with_photo3[0])
                    date_base(with_photo3, message.chat.id, text_hotels, bot.send_message, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста введите только цифрами, попробуйте еще раз&#10071',
                         parse_mode='HTML')
        bot.register_next_step_handler(message, ready_photo)


@bot.callback_query_handler(func=lambda call: call.data == 'Да')
def hotels_with_photos(call) -> None:
    bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за выбор!')
    bot.send_message(call.message.chat.id, 'Сколько фото Вам вывести (Не более 5)?')
    bot.register_next_step_handler(call.message, ready_photo)


@bot.callback_query_handler(func=lambda call: call.data == 'Нет')
def hotels_without_photos(call) -> None:
    """
    В зависимости от введенной команды пользователя выводим всю итоговую информацию по отелям без фотографий
    """
    bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за выбор!')
    bot.send_message(call.message.chat.id, 'Подождите пожалуйcта, идет обработка результата &#9203', parse_mode='HTML')
    search_hotels = SearchObject(search_hotel(User.dct[call.message.chat.id].call_data), config.search_list)
    if User.dct[call.message.chat.id].command == '/lowprice':
        text_hotels = ''
        for no_photo1 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                               User.dct[call.message.chat.id].check_in,
                                                               User.dct[call.message.chat.id].check_out,
                                                               User.dct[call.message.chat.id].count_hotels), False):
            text_hotels += f'{no_photo1[0]}\n'
            bot.send_message(call.message.chat.id, no_photo1[0], disable_web_page_preview=True, parse_mode='HTML')
            date_base(no_photo1, call.message.chat.id, text_hotels, bot.send_message, call.message.chat.id)
    elif User.dct[call.message.chat.id].command == '/highprice':
        text_hotels = ''
        for no_photo2 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                               User.dct[call.message.chat.id].check_in,
                                                               User.dct[call.message.chat.id].check_out,
                                                               User.dct[call.message.chat.id].count_hotels,
                                                               sort_price=False), False):
            text_hotels += f'{no_photo2[0]}\n'
            bot.send_message(call.message.chat.id, no_photo2[0], disable_web_page_preview=True, parse_mode='HTML')
            date_base(no_photo2, call.message.chat.id, text_hotels, bot.send_message, call.message.chat.id)
    else:
        text_hotels = ''
        for no_photo3 in text_transformation(property_founding(search_hotels.request_to_api(),
                                                               User.dct[call.message.chat.id].check_in,
                                                               User.dct[call.message.chat.id].check_out,
                                                               User.dct[call.message.chat.id].count_hotels,
                                                               price_r=User.dct[call.message.chat.id].price,
                                                               distance_c=User.dct[
                                                                   call.message.chat.id].distance), False):
            text_hotels += f'{no_photo3[0]}\n'
            bot.send_message(call.message.chat.id, no_photo3[0], disable_web_page_preview=True, parse_mode='HTML')
            date_base(no_photo3, call.message.chat.id, text_hotels, bot.send_message, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def question_date(call) -> None:
    """
    В зависимости от того, какую кнопку нажал пользователь, получаем id местоположения и записываем его в словарь,
    далее запрашиваем желаемую дату въезда в отель с помошью календаря
    """
    bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за выбор!')
    User.dct[call.message.chat.id].call_data = call.data
    calendar, step = DetailedTelegramCalendar(calendar_id='entry', locale='ru').build()
    bot.send_message(call.message.chat.id, f"Выберите желаемую дату въезда", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='entry'))
def date_entry(call) -> None:
    """
    Тут происходит взаимодействие с календарем, так же записываем в словарь дату въезда из отеля
    """
    result, key, step = DetailedTelegramCalendar(calendar_id='entry', locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите желаемую дату въезда",
                              call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваша дата въезда {result}", call.message.chat.id, call.message.message_id)
        User.dct[call.message.chat.id].check_in = str(result)
        calendar, step = DetailedTelegramCalendar(calendar_id='exit', locale='ru').build()
        bot.send_message(call.message.chat.id, f"Выберите желаемую дату выезда", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='exit'))
def departure_date(call) -> None:
    """
    Здесь происходит взаимодействие с календарем, так же записываем в словарь дату выезда из отеля и после, в
    зависимости от команды пользователя задаем вопрос для прохождения дальнейшего сценария
    """
    result, key, step = DetailedTelegramCalendar(calendar_id='exit', locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите желаемую дату выезда",
                              call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваша дата выезда {result}", call.message.chat.id, call.message.message_id)
        User.dct[call.message.chat.id].check_out = str(result)
        if User.dct[call.message.chat.id].command == '/lowprice' \
                or User.dct[call.message.chat.id].command == '/highprice':
            bot.send_message(call.message.chat.id, 'Сколько отелей вывести (Не более 10)?')
            bot.register_next_step_handler(call.message, question_about_photo)
        else:
            bot.send_message(call.message.chat.id, 'Введите пожалуйста желаемый диапазон цен'
                                                   ' за отель через пробел (руб)')
            bot.register_next_step_handler(call.message, price_range)
