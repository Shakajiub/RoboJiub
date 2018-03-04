import json

from sys import exc_info

def command(args):
    """Add/remove/edit the commands found in the custom commands json."""
    usage = "usage: s!command (add/edit/remove) (cmd) (...)"

    if len(args[2]) < 3:
        return usage

    queue = args[0]
    viewer = args[1]
    message = args[2]

    cmds = None
    try:
        with open('custom.json', 'r') as cmd_file:
            cmds = json.load(cmd_file)
    except Exception:
        queue.put(("{0}".format(exc_info()[0]), 'BG_error'))
        queue.put(("command() - Could not load json!", 'BG_error'))
        return None

    key = message[2]

    # Example: "s!command add hello Hello world!"
    # This will create the command "s!hello", which will return "Hello world!"
    if message[1] == "add":
        if len(message) < 4:
            return usage
        if key in cmds:
            return '@{0} - The command "{1}" already exists. Use "s!command edit (...)" to modify it.'.format(viewer, key)
        return add_command(cmds, key, message, viewer)

    # Example: "s!command edit hello yo yo yo"
    # Now the "s!hello" command will return "yo yo yo"
    elif message[1] == "edit":
        if len(message) < 4:
            return usage
        if key not in cmds:
            return '@{0} - Cannot find that command. Use "s!command add (...)" to create it.'.format(viewer)
        return add_command(cmds, key, message, viewer)

    # Example: "s!command remove hello"
    # And the command is no more
    elif message[1] == "remove":
        if key not in cmds:
            return "@{0} - Cannot find that command. It's already gone!".format(viewer)
        del cmds[key]
        with open('custom.json', 'w') as cmd_file:
            json.dump(cmds, cmd_file, indent=4, sort_keys=True)
        return '@{0} - Command "{1}" removed!'.format(viewer, key)

    return usage

def add_command(cmds, key, message, viewer):
    """Add the given key/message into the commands json and dump it."""
    del message[0] # "s!command"
    del message[0] # "add/edit"
    del message[0] # "(cmd)"
    value = " ".join(message)

    cmds[key] = value
    with open('custom.json', 'w') as cmd_file:
        json.dump(cmds, cmd_file, indent=4, sort_keys=True)
    return '@{0} - Command "{1}" saved!'.format(viewer, key)
