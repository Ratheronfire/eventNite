import json
import os
from json import JSONDecodeError
from pathlib import Path


def cwd() -> Path:
    return Path(os.path.abspath(__file__)).parent.parent


def data_folder() -> Path:
    return Path(cwd(), 'data')


def read_event_file():
    event_path = Path(data_folder(), 'events.json')

    if not os.path.isfile(event_path):
        return []

    with open(event_path, 'r') as event_file:
        return json.loads(event_file.read())


def write_event_file(data):
    event_path = Path(data_folder(), 'events.json')

    try:
        json.dumps(data)
    except JSONDecodeError:
        return  # Testing if we can parse the data before trying to write it.

    with open(event_path, 'w') as event_file:
        event_file.write(json.dumps(data))
