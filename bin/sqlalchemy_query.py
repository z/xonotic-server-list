from sqlalchemy_base import Stats, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///resources/data/stats.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

session.query(Stats).all()

stats = session.query(Stats).first()
print(stats.total_players)
