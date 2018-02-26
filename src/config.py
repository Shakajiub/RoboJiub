import json

global config
config = None

def get_config(force_reload=False):
    """Get the main json config file. Load it if first time or forced."""
    # TODO - Don't return the entire config, just a specific value
    global config
    if config == None or force_reload:
        with open('config.json') as config_file:
            config = json.load(config_file)
    return config

def get_botname():
    """Get the name of the bot as set up in the config."""
    botname = "botname"
    try:
        botname = get_config()['irc']['username']
    except KeyError:
        self.queue.put(("config.get_botname() - IRC config is corrupted!", 'BG_error'))
    return botname

def get_channel():
    """Get the name of the main channel as set up in the config."""
    channel = None
    try:
        channel = get_config()['irc']['channel']
    except KeyError:
        self.queue.put(("config.get_channel() - IRC config is corrupted!", 'BG_error'))
    return channel
