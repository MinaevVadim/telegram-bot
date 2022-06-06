from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from loguru import logger
from typing import Optional


@logger.catch()
def city_markup(found_cities) -> Optional[InlineKeyboardMarkup]:
    """
    Функция по созданию клавиатуры в телеграм боте. Итерируемся по ключу destination_id и добавляем кнопки

    :param found_cities: список словарей с нужным именем и id
    :rtype: list
    :return: destinations
    :rtype: InlineKeyboardMarkup, None
    """

    destinations = InlineKeyboardMarkup()
    lst = []
    for city in found_cities:
        try:
            lst.append(city["destination_id"])
            destinations.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'{city["destination_id"]}'))
        except KeyError as scx:
            logger.error(scx)
    if len(lst) >= 1:
        return destinations
    else:
        return None


@logger.catch()
def keyboard_for_id() -> InlineKeyboardMarkup:
    """
    Функция по созданию клавиатуры в телеграм боте

    :return: key_board
    :rtype: InlineKeyboardMarkup
    """

    key_board = InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='Да')
    key_board.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='Нет')
    key_board.add(key_no)
    return key_board
