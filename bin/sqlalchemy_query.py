from sqlalchemy_base import Stats, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///resources/data/stats.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()
# Make a query to find all Persons in the database
session.query(Stats).all()

# Return the first Person from all Persons in the database
stats = session.query(Stats).first()
print(stats.total_players)
