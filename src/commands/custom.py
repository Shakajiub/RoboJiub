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

    message = args[2]
    cmd = message[1]
    replace = []

    if len(args[2]) > 2:
        del message[0]
        del message[0]
        replace = message

    try:
        return custom_commands[cmd].format(*replace, msg=" ".join(replace))
    except KeyError: # Specified command does not exist
        return None
