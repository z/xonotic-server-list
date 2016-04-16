import falcon
import json
import calendar
from falcon_cors import CORS
from datetime import datetime
from bin.sqlalchemy_base import Stats, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bin.util import *


def row2json(row):
    unix_time = calendar.timegm(row.time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'total_players': row.total_players,
        'total_bots': row.total_bots,
        'countries': row.countries,
    }

    return datapoint


class PlayerStatsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""

        stats = session.query(Stats).all()

        # stats = session.query(Stats) \
        #     .filter_by(hour=13) \
        #     .all()

        data = []
        for row in stats:
            datapoint = row2json(row)

            data.append(datapoint)

        json_out = {'data': data}

        resp.body = json.dumps(json_out)


config = read_config('config/config.ini')

engine = create_engine(config['stats_database'])
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

cors = CORS(allow_origins_list=[config['frontend_url']])
api = falcon.API(middleware=[cors.middleware])
api.add_route('/player_stats', PlayerStatsResource())