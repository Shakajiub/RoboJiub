def command(args):
    """Add/remove/edit the commands found in the custom commands json."""
    usage = "usage: s!command (add/edit/remove) (cmd) ..."

    queue = args[0]
    viewer = args[1]
    message = args[2]

    quotes = None
    try:
        with open('custom.json', 'r') as quotes_file:
            quotes = json.load(quotes_file)
    except Exception:
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("command() - Could not load json!", 'BG_error'))
        return None

    # TODO - This command
