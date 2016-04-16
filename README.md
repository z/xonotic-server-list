# xonotic-server-list

Provide server list front-end and display player count stats over time.

## Frontend

Coming soon.

## Backend/Middleware

The heavy lifting is handled by code that acts as middleware between the
master server and the xonotic-server-list front-end. The master server
exposes a few ways to query qstat, returning xml, which the middleware
converts to JSON.  

### Installation

Setup a venv and install the requirements:

```
virtualenv -p /usr/bin/python3 venv
ln -s venv/bin/activate
source activate
pip install -r requirements.txt
```

### Configuration

Create a configuration file:

```
cp config/example.config.ini config/config.ini
```

Its contents should appear similar to below:

```ini
[default]
master_server = dpmaster.deathmask.net
stats_file = resources/data/stats.json
ip_location_db = resources/data/GeoLite2-Country.mmdb
```

### Usage

Print current stats to output:

```
./bin/players2json.py -o
```

Write current stats to output (appends to file or database):

```
./bin/players2json.py -w json
./bin/players2json.py -w db
```


See help for additional options:

```
./bin/players2json.py -h
```

The generated json is an array of objects padded by a `data` object.

```json
{
    "data": [
        {
            "time": 1460344051,
            "total_players": 30,
            "countries": {
                "EUR": 20,
                "AUS": 2,
                "USA": 8
            }
        },
        …
    ]
}
```

#### Development

The object looks similar to the example below:

**Note: the players value returns `None`, this is a bug. numplayers is used instead.**

```
{'@type': 'Q3S',
 '@address': '142.4.214.189:26010',
 '@status': 'UP',
 'hostname': '142.4.214.189:26010',
 'name': '(SMB) '
         'USA '
         'Instagib+Hook '
         'CTF/DM '
         '[DALLAS]',
 'gametype': None,
 'map': 'concrete_space_xon',
 'numplayers': '9',
 'maxplayers': '64',
 'ping': '28',
 'retries': '0',
 'rules': {'rule': [{'@name': 'gamename',
                     '#text': 'Xonotic'},
                    {'@name': 'modname',
                     '#text': 'data_insta'},
                    {'@name': 'gameversion',
                     '#text': '801'},
                    {'@name': 'bots',
                     '#text': '0'},
                    {'@name': 'protocol',
                     '#text': '3'},
                    {'@name': 'qcstatus',
                     '#text': 'ctf:git:P56:S55:F7:MInstaGib::score!!:caps!!:5:7:14:4'},
                    {'@name': 'd0_blind_id',
                     '#text': '1 '
                              '7hWPnEroUpCzlCIiQ4d0/U/4/hKFj9VjElarGFZayKw=@Xon//KssdlzGkFKdnnN4sgg8H+koTbBn5JTi37BAW1Q= '
                              '@~XHub/MCjSOklCBU4ADlHX3+EcTjC0xhJ6odguyTvGp0='}]},
 'players': None}
```

#### Attribution

This software includes GeoLite2 data created by MaxMind, available from
[maxmind.com](http://www.maxmind.com).
