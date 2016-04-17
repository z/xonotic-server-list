import os
import sys
import json
import datetime
import sqlalchemy as sqla
from sqlalchemy.ext import mutable
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
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

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    hour = Column(Integer, index=True)
    weekday = Column(Integer, index=True)
    countries = Column(JsonEncodedDict)
    total_players = Column(Integer)
    total_bots = Column(Integer)
    moving_average = Column(Float)


class Servers(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    period = Column(Integer)
    key = Column(String)
    name = Column(String)
    address = Column(String)
    total_players = Column(Integer)
    max_players = Column(Integer)
    map = Column(String)
    gametype = Column(String)
    ping = Column(Integer)
    modname = Column(String)
    version = Column(String)
    qcstatus = Column(String)
    players = Column(String)

engine = create_engine('sqlite:///resources/data/stats.db')
Base.metadata.create_all(engine)
