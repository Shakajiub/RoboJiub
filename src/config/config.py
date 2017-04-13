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

def get_botname():
    botname = "botname"
    try:
        botname = get_config()['irc']['username']
    except KeyError:
        self.queue.put(("config.get_botname() - IRC config is corrupted", 'BG_error'))
    return botname
