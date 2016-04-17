import falcon
import json
import calendar
import os
from falcon_cors import CORS
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

from bin.sqlalchemy_base import Stats, Base
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

        stats = session.query(Stats)

        if 'day' in req.params:
            filter = int_or_false(req.params['day'])
            if 0 <= filter <= 7:
                stats = stats.filter_by(weekday=filter)

        if 'hour' in req.params:
            filter = int_or_false(req.params['hour'])
            if 0 <= filter <= 24:
                stats = stats.filter_by(hour=filter)

        stats = stats.limit(288)

        data = []
        for row in stats:
            datapoint = row2json(row)

            data.append(datapoint)

        json_out = {'data': data}

        resp.body = json.dumps(json_out)


config = read_config(root_dir + '/config/config.ini')

engine = create_engine(config['stats_database'])
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

cors = CORS(allow_origins_list=[config['frontend_url']])
api = application = falcon.API(middleware=[cors.middleware])
api.add_route('/player_stats', PlayerStatsResource())
