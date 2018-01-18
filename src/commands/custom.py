import json

def custom(args):
    custom_commands = None
    try:
        with open('custom.json') as custom_file:
            custom_commands = json.load(custom_file)
    except Exception:
        return None

    cmd = args[2][1]
    try:
        return "{0}".format(custom_commands[cmd])
    except KeyError:
        return None
