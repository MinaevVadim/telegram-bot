import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
search_location = 'https://hotels4.p.rapidapi.com/locations/v2/search'
search_list = 'https://hotels4.p.rapidapi.com/properties/list'
get_photo = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
DEFAULT_COMMANDS = (
    ('help', "помощь по командам бота"),
    ('lowprice', "вывод самых дешёвых отелей в городе"),
    ('highprice', "вывод самых дорогих отелей в городе"),
    ('bestdeal', "вывод отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "вывод истории поиска отелей")
)
