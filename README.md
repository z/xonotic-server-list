# xonotic-server-list

Provide server list front-end and display player count stats over time.

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
stats_database = sqlite:///resources/data/stats.db
stats_file = resources/data/stats.json
ip_location_db = resources/data/GeoLite2-Country.mmdb
frontend_url = http://localhost:8003
```

### Usage

#### Collecting Data

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

#### Getting Data (API)

Setup the database:

```
python bin/sqlachemy_base.py
```

Run with gunicorn

```
gunicorn bin.api:api
```

#### Endpoints


###### /player_stats

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

###### /server_list

```
{
    "data": [
        {
            "max_players": 20,
            "country": "FR",
            "ping": 121,
            "time": 1460939412,
            "gametype": "dm",
            "map": "q3dm17ish",
            "name": "Jeff &amp; Julius Resurrection Server",
            "modname": "NewToys",
            "address": "91.121.112.160:26015",
            "total_players": 4,
            "version": "git"
        },
        …
    ]
}        
```

## Front-end

Everything in the `web` folder is static content without a dynamic server-side language. This can be served with nginx for example.

### Configuration

Copy the example config file:

```
cd web
cp static/js/example.config.js static/js/config.js
```

### Usage

Development:

```
cd web
python -m SimpleHTTPServer 8003
```

## Development

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

## Attribution

This software includes GeoLite2 data created by MaxMind, available from
[maxmind.com](http://www.maxmind.com).
