import json

global config
config = None

def get_config(force_reload=False):
    """TODO docstring."""
    global config

    if config == None or force_reload:
        with open('config.json') as config_file:
            config = json.load(config_file)

    return config
