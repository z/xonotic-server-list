#!/usr/bin/env python3
# JSON Player Middleware for qstat
# z@xnz.me

import time
import argparse
import locale
import geoip2.database
import calendar
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_base import Stats, Base

from util import *

locale.setlocale(locale.LC_ALL, '')


def main():

    args = parse_args()
    config = read_config('config/config.ini')

    total_players, total_bots, countries = get_player_counts(config, args)

    total_players_pretty = locale.format("%d", total_players, grouping=True)
    total_bots_pretty = locale.format("%d", total_bots, grouping=True)

    utc_time = datetime.utcnow()
    unix_time = calendar.timegm(utc_time.utctimetuple())

    datapoint = {
        'time': unix_time,
        'total_players': total_players,
        'total_bots': total_bots,
        'countries': countries,
    }

    if args.verbose:
        print('Total Players: ' + total_players_pretty)
        print('Total Bots: ' + total_bots_pretty)

    if args.write == 'db':
        engine = create_engine(config['stats_database'])
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        weekday = utc_time.weekday()
        hour = utc_time.strftime("%H")

        new_stats = Stats(
            countries=countries,
            total_players=total_players,
            total_bots=total_bots,
            moving_average=0,
            hour=hour,
            weekday=weekday
        )
        session.add(new_stats)
        session.commit()

    stats_json_file = config['stats_file']

    if os.path.isfile(stats_json_file):

        stats_json = read_json_file(stats_json_file)
        stats_json.append(datapoint)

        output = {}
        output['data'] = stats_json

    else:
        output = {}
        output['data'] = [datapoint]

    if args.output:
        if args.all:
            print(json.dumps(output))
        else:
            print(json.dumps(datapoint))

    if args.write == 'json':
        write_to_json(output, config['stats_file'])


def get_player_counts(config, args):

    reader = geoip2.database.Reader(config['ip_location_db'])

    xonotic_status = get_master_server(config['master_server'], 'xonotic')

    total_players = 0
    total_bots = 0
    countries = {}

    if 'server' in xonotic_status['qstat']:
        for server in xonotic_status['qstat']['server']:
            if 'numplayers' in server:

                server_players = int(server['numplayers'])
                server_bots = 0

                if 'rules' in server:
                    for rule in server['rules']['rule']:
                        if rule['@name'] == 'bots':
                            server_bots += int(rule['#text'])

                server_players = server_players - server_bots
                total_players += int(server_players)

                if server_players > 0 and '@address' in server:
                    ip = server['@address'].split(':')[0]
                    if is_valid_ip(ip):
                        response = reader.country(ip)
                        country = response.country.iso_code
                        if country in countries:
                            countries[country] += server_players
                        else:
                            countries[country] = server_players

                        if args.verbose:
                            print('Ip Address: ' + ip + ' Country: ' + response.country.iso_code)

    return total_players, total_bots, countries


def get_master_server(master_server, game):

    url = 'http://' + master_server + '/?xml=1&game=' + game
    data = api_request(url, format='xml')

    return data


def parse_args():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--output', '-o', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--all', '-a', action='store_true', help='Output all stats JSON to stdout')
    parser.add_argument('--verbose', '-v', action='store_true', help='Pretty during processing stats to stdout')
    parser.add_argument('--write', '-w', nargs='?', help='Write to JSON file or database defined in config.ini. Options: (db|json)')
    return parser.parse_args()


if __name__ == "__main__":
    main()
