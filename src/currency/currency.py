import os
import json

from urllib2 import urlopen
from src.config.config import get_config

def check_viewer_exists(viewer):
    """Return true if we have a json file for given viewer."""
    return os.path.isfile('./viewers/' + viewer + '.json')

def create_viewer(viewer, queue, bonus=0):
    """Create a json file for a new viewer."""
    try:
        with open('./viewers/' + viewer + '.json', 'w') as f:
            try:
                data = { 'currency': get_config()['currency']['startwith'] + bonus }
            except KeyError:
                queue.put(("create_viewer() - Currency config is corrupted", 'BG_error'))
                data = { 'currency': bonus }
            json.dump(data, f)
    except IOError:
        queue.put(("create_viewer() - Could not create json file for '{0}'".format(viewer), 'BG_error'))

def delete_viewer(viewer):
    """Delete the json file of given viewer if it exists."""
    if check_viewer_exists(viewer):
        os.remove('./viewers/' + viewer + '.json')

def award_viewer(viewer, amount, queue):
    """Award given viewer with given amount of currency. Create json file if necessary."""
    if not check_viewer_exists(viewer):
        create_viewer(viewer, queue)
    try:
        with open('./viewers/' + viewer + '.json', 'r+') as f:
            data = json.load(f)
            try:
                data['currency'] += amount
                f.seek(0)
                json.dump(data, f)
                f.truncate()
            except KeyError:
                queue.put(("award_viewer() - Corrupted json file for '{0}'".format(viewer), 'BG_error'))
                delete_viewer(viewer)
                create_viewer(viewer, queue, amount)
    except IOError:
        queue.put(("award_viewer() - Could not open json file for '{0}'".format(viewer), 'BG_error'))

def award_all_viewers(amount, queue):
    """Fetch the viewer list and award everyone with given amount of currency."""
    config = get_config()
    try:
        channel = config['irc']['channel'].replace('#', '')
        response = urlopen('http://tmi.twitch.tv/group/user/{0}/chatters'.format(channel))
        parsed_json = json.loads(response.read())

        for category in parsed_json['chatters']:
            for viewer in parsed_json['chatters'][category]:
                award_viewer(viewer, amount, queue)
    except KeyError:
        queue.put(("award_all_viewers() - IRC config is corrupted", 'BG_error'))

def get_viewer_value(viewer, queue, key, retry=0):
    """Return the value of given key in the json file of given viewer."""
    if retry > 1:
        queue.put(("get_viewer_value() - Something went seriously wrong", 'BG_error'))
        return False
    config = get_config()
    if not check_viewer_exists(viewer):
        create_viewer(viewer, queue)
        return get_viewer_value(viewer, queue, key, retry + 1)
    try:
        with open('./viewers/' + viewer + '.json', 'r') as f:
            data = json.load(f)
            try:
                value = data.get(key)
                return value
            except KeyError:
                queue.put(("get_viewer_value() - Corrupted json file for '{0}'".format(viewer), 'BG_error'))
                delete_viewer(viewer)
                create_viewer(viewer, queue)
                return get_viewer_value(viewer, queue, key, retry + 1)
    except IOError:
        queue.put(("get_viewer_value() - Could not open json file for '{0}'".format(viewer), 'BG_error'))
        return get_viewer_value(viewer, queue, key, retry + 1)
