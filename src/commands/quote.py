import sys
import json

from datetime import datetime

def quote(args):
    """Save a quote or reference an old one."""
    usage = "usage: s!quote (number)"

    if len(args[2]) < 2:
        return usage

    queue = args[0]
    viewer = args[1]
    message = args[2]

    quotes = None

    if message[1] in ["edit", "remove"]:
        return "TODO"

    elif message[1].isdigit():
        try:
            with open('quotes.json', 'r') as quotes_file:
                quotes = json.load(quotes_file)
            if quotes[message[1]]:
                return "Quote #{0}: {1}".format(message[1], quotes[message[1]])
            else: return "Sorry, I could not find that quote."
        except Exception:
            return "Sorry, I could not find that quote."

    elif message[1] != "add":
        return usage

    try:
        with open('quotes.json', 'r') as quotes_file:
            quotes = json.load(quotes_file)
    except Exception:
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("quotes() - Could not load json", 'BG_error'))
        return None

    del message[0]
    del message[0]
    quote = " ".join(message)

    num = len(quotes)
    date = datetime.now()
    quotes[num] = '"' + quote + '" [' + date.strftime('%Y-%m-%d') + ']'

    with open('quotes.json', 'w') as quotes_file:
        json.dump(quotes, quotes_file)

    return "{0} - Quote #{1} saved!".format(viewer, num)
