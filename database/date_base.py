from peewee import *


db = SqliteDatabase('people.db')


class Person(Model):
    command = CharField()
    date = CharField()
    hotels = CharField()

    class Meta:
        database = db


with db:
    Person.create_table()


def base_date_orm(commands, dates, hotels_all):
    with db:
        return Person.create(command=commands, date=dates, hotels=hotels_all)







