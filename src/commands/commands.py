import json
from src.config.config import get_config

def commands(args):
    """Return a list of all enabled commands for the channel."""
    #usage = "usage: s!commands"

    cmds = "[prefix: s!] - "
    config = get_config()

    custom_commands = None
    try:
        with open('custom.json') as custom_file:
            custom_commands = json.load(custom_file)
    except Exception:
        queue = args[0]
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("commands() - Could not load json!", 'BG_error'))
        return None

    for cmd in config['commands']:
        if config['commands'][cmd]['enabled']:
            cmds = cmds + cmd + ", "

    if custom_commands != None:
        for cmd in custom_commands:
            cmds = cmds + cmd + ", "

    return cmds[:-2]
