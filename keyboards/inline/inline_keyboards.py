from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types


def city_markup(found_cities):
    destinations = InlineKeyboardMarkup()
    for city in found_cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'{city["destination_id"]}'))
    return destinations


def keyboards():
    key_board = InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='Да')
    key_board.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='Нет')
    key_board.add(key_no)
    return key_board