from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    bot.send_message(
        message.from_user.id,
        f"Здравствуйте, {message.from_user.full_name}! Вас приветствует БОТ"
        f" компании Too Easy Travel &#128640, помогу найти интересующие Вас отели! "
        f"Для выбора запросов нажмите /help",
        parse_mode='HTML'
    )

