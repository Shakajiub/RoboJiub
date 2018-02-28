import os
import json
import errno

from datetime import datetime
from src.config import get_config

global mods
mods = None

def get_mods():
    """Get the list of current moderators in the chat."""
    global mods
    if mods == None:
        mods = ["shakajiub", "robojiub"]
    return mods

def add_mod(username):
    """Append the given username to the moderator list."""
    global mods
    if mods == None:
        mods = ["shakajiub"]
    if username not in mods:
        mods.append(username)

def check_viewer_exists(viewer):
    """Check if we have a json file for given viewer."""
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
                queue.put(("create_viewer() - Currency config is corrupted!", 'BG_error'))
                data = { 'currency': bonus }
            date = datetime.now()
            data['created'] = date.strftime('%Y-%m-%d')
            data['warnings'] = 0
            json.dump(data, f)
    except IOError:
        queue.put(("create_viewer() - Could not create json file for '{0}'!".format(viewer), 'BG_error'))

def delete_viewer(viewer):
    """Delete the json file of given viewer if it exists."""
    if check_viewer_exists(viewer):
        os.remove('./viewers/' + viewer + '.json')

def get_viewer_value(viewer, queue, key):
    """Get the value of given key in the json file of given viewer."""
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
                queue.put(("get_viewer_value() - Invalid key '{0}'!".format(key), 'BG_error'))
    except IOError:
        queue.put(("get_viewer_value() - Could not open json file for '{0}'!".format(viewer), 'BG_error'))
    return None
