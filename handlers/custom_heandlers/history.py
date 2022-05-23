from database.date_base import Person
from loader import bot


@bot.message_handler(commands=['history'])
def send_album_with_text(message):
    for person in Person.select():
        s1, s2, s3 = f'Команда - {person.command}', f'Время введенной команды - {person.date}',\
                     f'Отели, которые были найдены - {person.hotels}'
        bot.send_message(message.chat.id, f'{s1, s2, s3}')
