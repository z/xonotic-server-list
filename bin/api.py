import falcon
import json
import calendar
import os
from falcon_cors import CORS
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc, desc

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

from bin.sqlalchemy_base import Stats, Servers, Base
from bin.util import *


def row2playerstats(row):
    unix_time = calendar.timegm(row.time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'total_players': row.total_players,
        'total_bots': row.total_bots,
        'countries': row.countries,
    }

    return datapoint


def row2serverlist(row):
    unix_time = calendar.timegm(row.time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'name': row.name,
        'address': row.address,
        'total_players': row.total_players,
        'max_players': row.max_players,
        'map': row.map,
        'gametype': row.gametype,
        'ping': row.ping,
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

        stats = stats.order_by(desc(Stats.id)).limit(288)

        data = []
        for row in stats:
            datapoint = row2playerstats(row)

            data.append(datapoint)

        json_out = {'data': data}

        resp.body = json.dumps(json_out)


class ServerListResource:
    def on_get(self, req, resp):
        """Handles GET requests"""

        servers = session.query(Servers)

        servers = servers.order_by(asc(Servers.ping)).limit(200)

        data = []
        for row in servers:
            datapoint = row2serverlist(row)

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
api.add_route('/server_list', ServerListResource())
