import json

def custom(args):
    """Check if the custom json contains a simple reply to viewer's message."""
    #usage = "usage: s![command]"

    custom_commands = None
    try:
        with open('custom.json') as custom_file:
            custom_commands = json.load(custom_file)
    except Exception:
        queue = args[0]
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("custom() - Could not load json", 'BG_error'))
        return None

    cmd = args[2][1]
    try:
        return "{0}".format(custom_commands[cmd])
    except KeyError:
        return None
