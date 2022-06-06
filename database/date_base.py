from peewee import *
from typing import Optional


db = SqliteDatabase('DBHistory.db')


class InfoHistory(Model):
    """ Класс базы данных, в котором мы задаем названия полей таблицы

    Attributes:
        id_name (str): id чата в телеграме
        command (str): введенная команда
        date (str): дата и время введенной команды
        hotels (str): найденные отели
    """

    id_name = CharField(null=False)
    command = CharField(null=False)
    date = CharField(null=False)
    hotels = CharField(null=True)

    class Meta:
        database = db


with db:
    InfoHistory.create_table()


def date_base(ph: int, mess1: Optional[int], txt: str, bot, mess2: object) -> None:
    """
    Функция для записывания информации по отелю в базу данных и вывода сообщения об успешном поиске
    """
    if ph[1] == 0:
        with db:
            dct_history[mess1].hotels = txt
            dct_history[mess1].save()
        bot(mess2, 'Отели успешно найдены! Чтобы вернуться в меню нажмите &#10145 /help', parse_mode='HTML')


dct_history = dict()





