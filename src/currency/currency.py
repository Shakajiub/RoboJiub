import json

from urllib2 import urlopen, URLError
from src.config import get_config
from src.viewers.viewers import *

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
                queue.put(("award_viewer() - Corrupted json file for '{0}'!".format(viewer), 'BG_error'))
                delete_viewer(viewer)
                create_viewer(viewer, queue, amount)
    except IOError:
        queue.put(("award_viewer() - Could not open json file for '{0}'!".format(viewer), 'BG_error'))

def award_all_viewers(amount, queue):
    """Fetch the viewer list (save the mods) and award everyone with given amount of currency."""
#    global mods
#    if mods == None:
#        mods = []
    config = get_config()
    try:
        channel = config['irc']['channel'].replace('#', '')
        response = urlopen('http://tmi.twitch.tv/group/user/{0}/chatters'.format(channel))
        parsed_json = json.loads(response.read())

        for category in parsed_json['chatters']:
            for viewer in parsed_json['chatters'][category]:
                award_viewer(viewer, amount, queue)
#                if category == "moderators":
#                    mods.append(viewer)
    except KeyError:
        queue.put(("award_all_viewers() - IRC config is corrupted!", 'BG_error'))
    except URLError:
        queue.put(("award_all_viewers() - Could not get user list!", 'BG_error'))

def get_currency(queue):
    """Return the name of the currency if it's enabled."""
    config = get_config()
    try:
        if not config['currency']['enabled']:
            return None
        return config['currency']['name']
    except KeyError:
        queue.put(("validate_currency() - Currency config is corrupted!", 'BG_error'))
    return None
