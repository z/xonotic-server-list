import falcon
import json
import datetime
import calendar
import sqlite3
import os
from falcon_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc, desc, func

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

from bin.sqlalchemy_base import Stats, Servers, Base, JsonEncodedDictMerge
from bin.util import *


def row2playerstats(row):
    unix_time = calendar.timegm(row.time.utctimetuple())

    try:
        countries = json.loads(row.countries)
    except TypeError or ValueError:
        countries = row.countries

    datapoint = {
        'time': unix_time,
        'total_players': row.total_players,
        'total_bots': row.total_bots,
        'countries': countries,
    }

    return datapoint


def row2serverlist(row):
    unix_time = calendar.timegm(row.time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'name': row.name,
        'address': row.address,
        'country': row.country,
        'total_players': row.total_players,
        'max_players': row.max_players,
        'map': row.map,
        'gametype': row.gametype,
        'ping': row.ping,
        'version': row.version,
        'modname': row.modname,
    }

    return datapoint


class PlayerStatsResource:

    def __init__(self, period='all'):
        self.period = period

    def on_get(self, req, resp):
        """Handles GET requests"""

        limit = 288

        if self.period != 'all':

            group_it_by = 'day'
            today = datetime.date.today()

            if self.period == 'week':
                group_it_by = 'hour, weekday'
                limit = 500
                duration = datetime.timedelta(days=7)

            if self.period == 'month':
                group_it_by = 'day'
                limit = 31
                duration = datetime.timedelta(days=31)

            start_date = today - duration

            stats = session.query(
                    Stats.hour.label('hour'),
                    Stats.weekday.label('weekday'),
                    func.avg(Stats.total_players).label('total_players'),
                    func.avg(Stats.total_bots).label('total_bots'),
                    func.min(Stats.time).label('time'),
                    # func.extract('month', Stats.time).label('month'),
                    # func.extract('week', Stats.time).label('week'),
                    func.extract('day', Stats.time).label('day'),
                    func.json_merge(Stats.countries).label('countries'),
                ) \
                .group_by(group_it_by) \
                .filter(Stats.time >= start_date)

            # stats = stats.group_by(Stats.time).filter(Stats.time >= '2016-06-18')
            # stats = stats.group_by(Stats.week)

        else:
            stats = session.query(Stats)

        if 'day' in req.params:
            filter = int_or_false(req.params['day'])
            if 0 <= filter <= 7:
                stats = stats.filter_by(weekday=filter)

        if 'hour' in req.params:
            filter = int_or_false(req.params['hour'])
            if 0 <= filter <= 24:
                stats = stats.filter_by(hour=filter)

        stats = stats.order_by(desc(Stats.id)).limit(limit)

        data = []
        for row in stats:

            if self.period == 'all':
                datapoint = row2playerstats(row)
            else:
                datapoint = row2playerstats(row)

            data.append(datapoint)

        json_out = {'data': data}

        resp.body = json.dumps(json_out)


class ServerListResource:

    def on_get(self, req, resp):
        """Handles GET requests"""

        last = session.query(Servers).order_by(Servers.period.desc()).first()

        servers = session.query(Servers)

        if last:
            servers = servers.filter_by(period=last.period)

        servers = servers.order_by(desc(Servers.total_players)).limit(200)

        data = []
        for row in servers:
            datapoint = row2serverlist(row)

            data.append(datapoint)

        json_out = {'data': data}

        resp.body = json.dumps(json_out)


config = read_config(root_dir + '/config/config.ini')


def sqlite_memory_engine_creator():
    global config
    con = sqlite3.connect(config['stats_database'].replace('sqlite:///', ''))
    con.create_aggregate('json_merge', 1, JsonEncodedDictMerge)
    return con

engine = create_engine(config['stats_database'], creator=sqlite_memory_engine_creator)
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

cors = CORS(allow_origins_list=[config['frontend_url']])
api = application = falcon.API(middleware=[cors.middleware])
api.add_route('/player_stats/all', PlayerStatsResource('all'))
api.add_route('/player_stats/week', PlayerStatsResource('week'))
api.add_route('/player_stats/month', PlayerStatsResource('month'))
api.add_route('/server_list', ServerListResource())
