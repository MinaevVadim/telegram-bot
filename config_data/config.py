import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
RAPID_API_KEY: str = os.getenv('RAPID_API_KEY')
search_location: str = 'https://hotels4.p.rapidapi.com/locations/v2/search'
search_list: str = 'https://hotels4.p.rapidapi.com/properties/list'
get_photo: str = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
next_action = 'Отели были успешно найдены! Чтобы вернуться в меню нажмите &#10145 /help'
DEFAULT_COMMANDS: tuple = (
    ('help', "помощь по командам бота"),
    ('lowprice', "вывод самых дешёвых отелей в городе"),
    ('highprice', "вывод самых дорогих отелей в городе"),
    ('bestdeal', "вывод отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "вывод истории поиска отелей")
)
