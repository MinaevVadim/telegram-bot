from database.date_base import InfoHistory, db
from loader import bot


@bot.message_handler(commands=['history'])
def result_history(message) -> None:
    with db:
        InfoHistory.update(hotels='Отели не были найдены').where(InfoHistory.hotels == None).execute()
        for history in InfoHistory.select().where(InfoHistory.id_name == message.chat.id):
            bot.send_message(message.chat.id, (f'Команда:  {history.command}\n'
                                               f'Время введенной команды:  {history.date}\n'
                                               f'Отели, которые были найдены:\n\n{history.hotels}'),
                             disable_web_page_preview=True)







