import requests
import re
import json
import datetime
from telebot.types import InputMediaPhoto
from config_data import config


class SearchObject:

    def __init__(self, querystring, url):
        self.url = url
        self.querystring = querystring
        self.headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
                        "X-RapidAPI-Key": config.RAPID_API_KEY}

    def request_to_api(self):
        try:
            response = requests.get(self.url, headers=self.headers, params=self.querystring, timeout=10)
            if response.status_code == requests.codes.ok:
                return response.text
        except BaseException:
            return exit('Ошибка API')


def search_city(city):
    return {"query": city, "locale": "ru_RU", "currency": "RUB"}


def search_hotel(id_hotel):
    return {"destinationId": id_hotel, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
            "checkOut": "2020-01-15", "adults1": "1", "sortOrder":
                "PRICE", "locale": "ru_RU", "currency": "RUB"}


def search_photo(id_photo):
    return {"id": id_photo}


def property_founding(request, check_date, need_hotel, need_photo=5, price_r=None, distance_c=None, sort_price=True):
    """ Основная функция поиска отелей """

    find = re.search(r'(?<=,)"results":.+?(?=,"pagination")', request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")

        if sort_price is False:
            suggestions['results'].sort(key=lambda x: int(x["ratePlan"]["price"]["current"][:-3].replace(',', '')),
                                        reverse=True)
        else:
            suggestions['results'].sort(key=lambda x: int(x["ratePlan"]["price"]["current"][:-3].replace(',', '')),
                                        reverse=False)
        cities = list()
        count = 0
        for i in suggestions['results']:
            try:
                search_photos = SearchObject(search_photo(i['id']), config.get_photo)
                price_change = int((i["ratePlan"]["price"]["current"].replace(',', ''))[:-3])
                a = check_date[0].split('-')
                b = check_date[1].split('-')
                aa = datetime.date(int(a[0]), int(a[1]), int(a[2]))
                bb = datetime.date(int(b[0]), int(b[1]), int(b[2]))
                cc = str(abs(aa - bb))
                days = cc.split()[0]
                sum_count = str(price_change * int(days))
                found_path = {'Отель': i["name"], 'Адрес': i["address"]["streetAddress"],
                              'Стоимость за ночь': i["ratePlan"]["price"]["current"].replace('RUB', 'рублей'),
                              f'Стоимость за весь период проживания': f'{sum_count} рублей',
                              'До центра города': i['landmarks'][0]['distance'],
                              'Фото': photo_founding(search_photos.request_to_api(), need_photo)}
                if price_r is None and distance_c is None:
                    cities.append(found_path)
                    count += 1
                else:
                    if int(price_r[0]) <= price_change <= int(price_r[1]) and \
                            float(distance_c[0]) <= float((i['landmarks'][0]['distance'].replace(',', '.'))[:-2]) <= \
                            float(distance_c[1]):
                        cities.append(found_path)
                        count += 1
                    else:
                        continue
            except BaseException:
                exit('Ошибка при итерации отелей!')
            if count == 10 or count == need_hotel:
                break
        return cities
    return exit('Ошибка при поиске отелей!')


def text_transformation_photo(text, flag=True):
    """ Генератор для конечного выведения информации по отелям """

    text_ready = ''
    count = len(text)
    for i in text:
        count -= 1
        for i_m, k in i.items():
            if i_m != 'Фото':
                text_ready += f'{i_m}: {k}\n'
        if flag is True:
            yield [InputMediaPhoto(j, caption=text_ready) if s == 0 else InputMediaPhoto(j)
                   for s, j in enumerate(i['Фото'])], count
        elif flag is False:
            yield text_ready, count
        text_ready = ''
    return exit('Ошибка при трансформации текста!')


def photo_founding(request, count_photo):
    """ Функция по поиску фото отелей"""

    request = re.sub(r'{size}.jpg', 'y.jpg', request)
    find = re.search(r'(?<=,)"hotelImages":.+?(?=,"featuredImageTrackingDetails")', request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")

        photo = list()
        count = 0
        for i in suggestions['hotelImages']:
            try:
                photo.append(i["baseUrl"])
                count += 1
            except BaseException:
                continue
            if count == 8 or count == count_photo:
                break
        return photo
    return exit('Ошибка при нахождении фото!')


def city_founding(request):
    """ Функция по уточнению местоположения отеля """

    find = re.search(r'(?<="CITY_GROUP",).+?[\]]', request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = [{'city_name': i['name'], 'destination_id': i['destinationId']} for i in suggestions['entities']]
        return cities
    return exit('Ошибка при уточнении местоположения!')
