from telebot import types


class User:
    """ Класс состояния пользователя """

    dct = dict()

    def __init__(self):
        self.command = None
        self.date = None
        self.hotels = None
        self.count_photos = None
        self.count_hotels = None
        self.call_data = None
        self.price = None
        self.distance = None
        self.check_in_out = None
        self.text_hotels = None


