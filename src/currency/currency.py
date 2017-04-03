import os
import json

from urllib2 import urlopen
from src.config.config import get_config

def check_viewer_exists(viewer):
    """Return true if we have a json file for given viewer."""
    return os.path.isfile('./viewers/' + viewer + '.json')

def create_viewer(viewer, bonus=0):
    """Create a json file for a new viewer."""
    try:
        with open('./viewers/' + viewer + '.json', 'w') as f:
            try:
                data = { 'currency': get_config()['currency']['startwith'] + bonus }
            except KeyError:
                print("Could not find value 'startwith' in 'currency' config!")
                data = { 'currency': bonus }
            json.dump(data, f)
    except IOError:
        print("Could not create new json file for viewer '" + viewer + "'!")

def delete_viewer(viewer):
    """Delete the json file of given viewer if it exists."""
    if check_viewer_exists(viewer):
        os.remove('./viewers/' + viewer + '.json')

def award_viewer(viewer, amount):
    """Award given viewer with given amount of currency. Create json file if necessary."""
    if not check_viewer_exists(viewer):
        create_viewer(viewer)
    try:
        with open('./viewers/' + viewer + '.json', 'r+') as f:
            data = json.load(f)
            try:
                data['currency'] += amount
                f.seek(0)
                json.dump(data, f)
                f.truncate()
            except KeyError:
                print("Corrupted json file for viewer '" + viewer + "'!")
                delete_viewer(viewer)
                create_viewer(viewer, amount)
    except IOError:
        print("Could not open json file for viewer '" + viewer + "'!")

def award_all_viewers(amount):
    """Fetch the viewer list and award everyone with given amount of currency."""
    config = get_config()
    try:
        channel = config['irc']['channel'].replace('#', '')
        response = urlopen('http://tmi.twitch.tv/group/user/{0}/chatters'.format(channel))
        parsed_json = json.loads(response.read())

        for category in parsed_json['chatters']:
            for viewer in parsed_json['chatters'][category]:
                award_viewer(viewer, amount)
    except KeyError:
        print("Config file / fetched json file are missing keys!")

def get_viewer_value(viewer, key, retry=0):
    """Return the value of given key in the json file of given viewer."""
    if retry > 1:
        print("Something went seriously wrong in function get_viewer_value!")
        return False
    config = get_config()
    if not check_viewer_exists(viewer):
        create_viewer(viewer)
        return get_viewer_value(viewer, key, retry + 1)
    try:
        with open('./viewers/' + viewer + '.json', 'r') as f:
            data = json.load(f)
            try:
                value = data.get(key)
                return value
            except KeyError:
                print("Corrupted json file for viewer '" + viewer + "'!")
                delete_viewer(viewer)
                create_viewer(viewer)
                return get_viewer_value(viewer, key, retry + 1)
    except IOError:
        print("Could not open json file for viewer '" + viewer + "'!")
        return get_viewer_value(viewer, key, retry + 1)
