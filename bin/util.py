import os
import json
import configparser
import urllib.request
import xmltodict
import re
from shutil import copyfile


def write_to_json(output, file):

    check_if_not_create(file)

    f = open(file, 'w')
    f.write(json.dumps(output))
    f.close()


def read_json_file(file):

    f = open(file)
    data = f.read()
    stats_json = json.loads(data)['data']
    f.close()

    return stats_json


def check_if_not_create(file, template=None):
    if not os.path.isfile(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        if template:
            copyfile(template, file)
        else:
            fo = open(file, 'w')
            fo.write('')
            fo.close()


def api_request(url, format='json'):

    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    raw_data = response.read()
    decoded = raw_data.decode("utf-8")

    if format == 'xml':
        data = xmltodict.parse(decoded)
    else:
        data = json.loads(decoded)

    return data


def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))


def read_config(config_file):

    if not os.path.isfile(config_file):
        print(config_file + ' not found, please create one.')
        return False

    config = configparser.ConfigParser()
    config.read(config_file)

    return config['default']