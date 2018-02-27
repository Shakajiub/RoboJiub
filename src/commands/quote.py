import sys
import json

from random import choice
from datetime import datetime
from src.viewers.viewers import get_mods

def quote(args):
    """Save a quote or reference an old one."""
    usage = "usage: s!quote (ID/text)"

    queue = args[0]
    viewer = args[1]
    message = args[2]

    quotes = None
    try:
        with open('quotes.json', 'r') as quotes_file:
            quotes = json.load(quotes_file)
    except Exception:
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("quotes() - Could not load json!", 'BG_error'))
        return None

    response = "Sorry, I could not find that quote."

    if len(args[2]) == 1: # Get a random quote
        try:
            key = choice(quotes.keys())
            return "Quote #{0}: {1}".format(key, quotes[key])
        except Exception:
            return response

    elif message[1].isdigit(): # Get a quote by ID
        try:
            return "Quote #{0}: {1}".format(message[1], quotes[message[1]])
        except Exception:
            return response

    elif message[1] not in ["add", "edit", "remove"]: # Get a quote that contains given text
        del message[0] # "s!quote"
        for quote in quotes:
            if " ".join(message) in quotes[quote]:
                response = "Quote #{0}: {1}".format(quote, quotes[quote])
                break
        return response

    if viewer not in get_mods(): # Only moderators can access the advanced commands below
        return None

    if message[1] in ["edit", "remove"]:
        return "TODO"

    elif message[1] == "add":
        if len(message) < 3:
            return "usage: s!quote add (quote)"

        del message[0] # "s!quote"
        del message[0] # "add"
        quote = " ".join(message)

        num = len(quotes)
        date = datetime.now()
        quotes[num] = '"' + quote + '" [' + date.strftime('%Y-%m-%d') + ']'

        with open('quotes.json', 'w') as quotes_file:
            json.dump(quotes, quotes_file)
        return "{0} - Quote #{1} saved!".format(viewer, num)

    return None
