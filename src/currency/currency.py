import os
import json
import errno

from urllib2 import urlopen, URLError
from src.config.config import get_config

global mods
mods = None

def get_mods():
    """Return the list of current mods in the chat."""
    # TODO - Fetch the list if it's None (only during the first minute since bot launch)
    global mods
    if mods == None:
        mods = ["shakajiub", "robojiub"]
    return mods

def check_viewer_exists(viewer):
    """Return true if we have a json file for given viewer."""
    return os.path.isfile('./viewers/' + viewer + '.json')

def make_sure_path_exists(path):
    """Check if the given path exists on the system, if not, create it."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def create_viewer(viewer, queue, bonus=0):
    """Create a json file for a new viewer."""
    try:
        make_sure_path_exists('./viewers/')
        with open('./viewers/' + viewer + '.json', 'w') as f:
            try:
                data = { 'currency': get_config()['currency']['startwith'] + bonus }
            except KeyError:
                queue.put(("create_viewer() - Currency config is corrupted", 'BG_error'))
                data = { 'currency': bonus }
            json.dump(data, f)
    except IOError:
        queue.put(("create_viewer() - Could not create json file for '{0}'".format(
                    viewer), 'BG_error'))

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
                queue.put(("award_viewer() - Corrupted json file for '{0}'".format(
                            viewer), 'BG_error'))
                delete_viewer(viewer)
                create_viewer(viewer, queue, amount)
    except IOError:
        queue.put(("award_viewer() - Could not open json file for '{0}'".format(
                    viewer), 'BG_error'))

def award_all_viewers(amount, queue):
    """Fetch the viewer list and award everyone with given amount of currency."""
    global mods
    mods = []
    config = get_config()
    try:
        channel = config['irc']['channel'].replace('#', '')
        response = urlopen('http://tmi.twitch.tv/group/user/{0}/chatters'.format(channel))
        parsed_json = json.loads(response.read())

        for category in parsed_json['chatters']:
            for viewer in parsed_json['chatters'][category]:
                award_viewer(viewer, amount, queue)
                if category == "moderators":
                    mods.append(viewer)
    except KeyError:
        queue.put(("award_all_viewers() - IRC config is corrupted", 'BG_error'))
    except URLError:
        queue.put(("award_all_viewers() - Could not get user list", 'BG_error'))
    #queue.put(("Done!", 'BG_success'))

def get_viewer_value(viewer, queue, key):
    """Return the value of given key in the json file of given viewer."""
    config = get_config()
    if not check_viewer_exists(viewer):
        create_viewer(viewer, queue)
    try:
        with open('./viewers/' + viewer + '.json', 'r') as f:
            data = json.load(f)
            try:
                value = data.get(key)
                return value
            except KeyError:
                queue.put(("get_viewer_value() - Invalid key '{0}'".format(key), 'BG_error'))
    except IOError:
        queue.put(("get_viewer_value() - Could not open json file for '{0}'".format(
                    viewer), 'BG_error'))

def validate_currency(user_input, queue):
    """Return the name of the currency if it's enabled and given input is a digit."""
    config = get_config()
    try:
        if not config['currency']['enabled']:
            return None
        if not user_input.isdigit():
            return False
        return config['currency']['name']
    except KeyError:
        queue.put(("validate_currency() - Currency config is corrupted", 'BG_error'))
        return None
