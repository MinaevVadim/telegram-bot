import requests
import re
import json
import datetime
from telebot.types import InputMediaPhoto
from config_data import config
from typing import Optional, Union, Iterable
from loguru_for_me import logger_add
from loguru import logger


class SearchObject:
    """
    Класс по обработке запроса к API

    Args:
        querystring (str): словарь с параментрами необходимыми для поиска нужно информации в эндпоинте
        url (str): передается конкретный эндпоинт rapidapi
    """

    def __init__(self, querystring: str, url: str) -> None:
        self.url = url
        self.querystring = querystring
        self.headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
                        "X-RapidAPI-Key": config.RAPID_API_KEY}

    def request_to_api(self) -> Optional[str]:
        """ Метод запроса к API. Прежде чем десереализовать ответ в объект, обязательно
         происходит проверка на статус код """

        try:
            response = requests.get(self.url, headers=self.headers, params=self.querystring, timeout=10)
            if response.status_code == requests.codes.ok:
                return response.text
        except requests.exceptions.ConnectTimeout as scx:
            return logger.error(scx)


@logger.catch()
def search_city(city: str) -> Union[dict, str]:
    """
    Функция по установке нужных параметров (города) для дальнейшего поиска отелей

    :param city: город
    :rtype: str
    :return: dict
    :rtype: dict
    """

    return {"query": city, "locale": "ru_RU", "currency": "RUB"}


@logger.catch()
def search_hotel(id_hotel: str) -> Union[dict, str]:
    """
    Функция по установке нужных параметров (id отеля) для дальнейшего поиска отелей

    :param id_hotel: id отеля
    :rtype: str
    :return: dict
    :rtype: dict
    """

    return {"destinationId": id_hotel, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
            "checkOut": "2020-01-15", "adults1": "1", "sortOrder":
                "PRICE", "locale": "ru_RU", "currency": "RUB"}


@logger.catch()
def search_photo(id_photo: str) -> Union[dict, str]:
    """
    Функция по установке нужных параметров (id фото) для дальнейшего поиска отелей

    :param id_photo: id фото
    :rtype: str
    :return: dict
    :rtype: dict
    """

    return {"id": id_photo}


@logger.catch()
def property_founding(request: str, checkin: str, checkout: str, need_hotel: int,
                      need_photo=5, price_r=None, distance_c=None, sort_price=True) -> list:
    """
    Основная функция поиска отелей. Делаем проверку в тексте ответа регулярным выражением, а затем подгружаем json.
    Далее итерируемся по ключу results и добавляем в список нужную информацию по отелям и после сортируем получившийся
    результат по стоимости за ночь от большего к меньшему или наоборот в зависимости от команды, который ввел
    пользователь в телеграм боте

    :param request: запрос API
    :rtype: str
    :param checkin: дата въезда в отель
    :rtype: str
    :param checkout: дата выезда из отеля
    :rtype: str
    :param need_hotel: необходимое количеств отелей
    :rtype: int
    :param need_photo: необходимое количеств фото
    :rtype: int
    :param price_r: диапазон цен за отель
    :rtype: str, None
    :param distance_c: диапазон расстояния от отеля до центра
    :rtype: str, None
    :param sort_price: нужная сортировка по стоимости отелей
    :rtype: bool
    :return: hotels, []
    :rtype: list
    """

    find = re.search(r'(?<=,)"results":.+?(?=,"pagination")', request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")

        hotels = list()
        count = 0
        for i in suggestions['results']:
            try:
                search_photos = SearchObject(search_photo(i['id']), config.get_photo)
                price_change = int((i["ratePlan"]["price"]["current"].replace(',', ''))[:-3])
                checkin_list = checkin.split('-')
                checkout_list = checkout.split('-')
                datetime_checkin = datetime.date(int(checkin_list[0]), int(checkin_list[1]), int(checkin_list[2]))
                datetime_checkout = datetime.date(int(checkout_list[0]), int(checkout_list[1]), int(checkout_list[2]))
                calculating_date = str(abs(datetime_checkin - datetime_checkout))
                days = calculating_date.split()[0]
                sum_count = str(price_change * int(days))
                found_path = {'Отель': i["name"], 'Адрес': i["address"]["streetAddress"],
                              'Стоимость за ночь': f'{price_change} RUB',
                              f'Стоимость за весь период проживания': f'{sum_count} RUB',
                              'До центра города': i['landmarks'][0]['distance'],
                              'Страница отеля': f'https://www.hotels.com/ho{i["id"]}',
                              'Фото': photo_founding(search_photos.request_to_api(), need_photo)}
                if price_r is None and distance_c is None:
                    hotels.append(found_path)
                    count += 1
                else:
                    if int(price_r[0]) <= price_change <= int(price_r[1]) and \
                            float(distance_c[0]) <= float((i['landmarks'][0]['distance'].replace(',', '.'))[:-2]) <= \
                            float(distance_c[1]):
                        hotels.append(found_path)
                        count += 1
                    else:
                        continue
            except (TypeError, SyntaxError, KeyError, NameError, ValueError):
                continue
            if count == 10 or count == need_hotel:
                if len(hotels) != 0:
                    if sort_price is False:
                        hotels.sort(
                            key=lambda x: int(x['Стоимость за ночь'][:-6].replace(',', '')),
                            reverse=True)
                    else:
                        hotels.sort(
                            key=lambda x: int(x['Стоимость за ночь'][:-6].replace(',', '')),
                            reverse=False)
                    break
                else:
                    break
        return hotels
    return []


@logger.catch()
def text_transformation(text: list, flag=True) -> Optional[Iterable]:
    """
    Генератор для конечного выведения информации по отелям. Если в пераметр text передается пустой список,
    выводим информацию о том, что отели не были найдены, если же список не пустой, то итерируемся по нему выводя
    готовые данные по отелям с фото или без, в зависимости от параметра flag

    :param text: нужная сортировка по стоимости отелей
    :rtype: list
    :param flag: True - вывод отелей с фото, False - вывод отелей без фото
    :rtype: bool
    """

    if len(text) == 0:
        yield ['По вашему запросу отели не были найдены, чтобы вернуться в меню нажмите &#10145 /help', '.', '.', '.']
    else:
        text_ready = ''
        count = len(text)
        for i in text:
            count -= 1
            for i_m, k in i.items():
                if i_m != 'Фото':
                    text_ready += f'{i_m}: {k}\n'
            if flag is True:
                yield [InputMediaPhoto(j, caption=text_ready) if s == 0 else InputMediaPhoto(j)
                       for s, j in enumerate(i['Фото'])], count, text_ready
            elif flag is False:
                yield text_ready, count
            text_ready = ''
        return None


@logger.catch()
def photo_founding(request: Optional[str], count_photo: int) -> Optional[list]:
    """
    Функция по поиску фото отелей. Делаем проверку в тексте ответа регулярным выражением, а затем подгружаем json.
    Далее итерируемся по ключу hotelImages и добавляем в список фотографии отелей

    :param request: запрос API
    :rtype: str, None
    :param count_photo: количество фото
    :rtype: int
    :return: photo
    :rtype: list, None
    """

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
            except (TypeError, SyntaxError, KeyError, NameError, ValueError):
                continue
            if count == 5 or count == count_photo:
                break
        return photo
    return None


@logger.catch()
def city_founding(request: Optional[str]) -> Optional[list]:
    """
    Функция по уточнению местоположения отеля. Делаем проверку в тексте ответа регулярным выражением, а затем
    подгружаем json. Далее итерируемся по ключу entities и добавляем в список местоположения, так же пропускаем
    дублируюшие названия используя при этом дополнительный список, добовляя туда повторы

    :param request: запрос API
    :rtype: str, None
    :return: cities
    :rtype: list, None
     """

    find = re.search(r'(?<="CITY_GROUP",).+?[\]]', request)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        replay_id = list()
        for i in suggestions['entities']:
            try:
                if i['name'] in replay_id:
                    continue
                else:
                    cities.append({'city_name': i['name'], 'destination_id': i['destinationId']})
                    replay_id.append(i['name'])
            except (TypeError, SyntaxError, KeyError, NameError, ValueError):
                continue
        return cities
    return None
