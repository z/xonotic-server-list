import os
import sys
import json
import sqlalchemy as sqla
from sqlalchemy.ext import mutable
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class JsonEncodedDict(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.String

    def process_bind_param(self, value, dialect):
        if value:
            return json.dumps(value)
        else:
            return {}

    def process_result_value(self, value, dialect):
        if value:
            return json.loads(value)
        else:
            return {}


mutable.MutableDict.associate_with(JsonEncodedDict)


class Stats(Base):
    __tablename__ = 'stats'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    hour = Column(Integer, index=True)
    weekday = Column(Integer, index=True)
    countries = Column(JsonEncodedDict)
    total_players = Column(Integer)
    moving_average = Column(Float)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///resources/data/stats.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
