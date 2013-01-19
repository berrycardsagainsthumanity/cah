from sqlalchemy import MetaData, Table
from sqlalchemy.orm import mapper
from webroot.db import engine

meta = MetaData(bind=engine)

cards = Table('cards', meta, autoload=True)
cardset = Table('cardset', meta, autoload=True)

class Cards(object):
    pass

mapper(Cards, cards)


class CardSets(object):
    pass

mapper(CardSets, cardset)