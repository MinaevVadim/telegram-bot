class User:
    """ Класс состояния пользователя """

    dct = dict()

    def __init__(self) -> None:
        self.command = None
        self.id = None
        self.for_history = None
        self.hotels = None
        self.count_photos = None
        self.count_hotels = None
        self.call_data = None
        self.price = None
        self.distance = None
        self.check_in = None
        self.check_out = None


