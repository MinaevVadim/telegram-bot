from loguru import logger

logger.add(
    'hotels.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='10 MB',
    compression='zip'
)
