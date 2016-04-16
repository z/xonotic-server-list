from sqlalchemy_base import Stats, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import calendar
from datetime import datetime

engine = create_engine('sqlite:///resources/data/stats.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

stats = session.query(Stats).all()

json_out = [];

for row in stats:

    unix_time = calendar.timegm(row.time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'total_players': row.total_players,
        'total_bots': row.total_bots,
        'countries': row.countries,
    }

    json_out.append(datapoint)

print(json_out)
