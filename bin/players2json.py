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

from sqlalchemy_base import Stats, Servers, Base

from util import *

locale.setlocale(locale.LC_ALL, '')


def main():

    args = parse_args()
    config = read_config('config/config.ini')

    xonotic_status = get_master_server(config['master_server'], 'xonotic')

    total_players, total_bots, countries = get_player_counts(xonotic_status, config, args)

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

        if 'server' in xonotic_status['qstat']:

            reader = geoip2.database.Reader(config['ip_location_db'])

            last = session.query(Servers).order_by(Servers.period.desc()).first()
            if last:
                last_period = last.period + 1
            else:
                last_period = 0

            for server in xonotic_status['qstat']['server']:
                if 'numplayers' in server:

                    server_name = server['name']
                    server_address = server['@address']
                    server_ip = server['@address'].split(':')[0]
                    server_total_players = int(server['numplayers'])
                    server_max_players = int(server['maxplayers'])
                    server_ping = int(server['ping'])
                    server_map = server['map']

                    if is_valid_ip(server_ip):
                        response = reader.country(server_ip)
                        server_country = response.country.iso_code

                    if 'rules' in server:
                        for rule in server['rules']['rule']:

                            if rule['@name'] == 'qcstatus':
                                server_gametype = rule['#text'].split(':')[0]
                                server_version = rule['#text'].split(':')[1]
                                server_modname = rule['#text'].split(':')[5].lstrip('M')
                                server_qcstatus = rule['#text']

                            if rule['@name'] == 'd0_blind_id':
                                server_key = rule['#text']

                    new_server = Servers(
                        period=last_period,
                        key=server_key,
                        name=server_name,
                        address=server_address,
                        country=server_country,
                        total_players=server_total_players,
                        max_players=server_max_players,
                        ping=server_ping,
                        map=server_map,
                        gametype=server_gametype,
                        modname=server_modname,
                        version=server_version,
                        qcstatus=server_qcstatus
                    )
                    session.add(new_server)
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


def get_player_counts(data, config, args):

    reader = geoip2.database.Reader(config['ip_location_db'])

    total_players = 0
    total_bots = 0
    countries = {}

    if 'server' in data['qstat']:
        for server in data['qstat']['server']:
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
