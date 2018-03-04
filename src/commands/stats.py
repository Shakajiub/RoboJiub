from src.viewers.viewers import *
from src.currency.currency import *

def stats(args):
    """Return all information we have for the caller."""
    #usage = "usage: s!stats (viewer)"

    # TODO - Return some unique info when returning stats for the bot

    queue = args[0]
    viewer = args[1]
    target = viewer

    start = "@{0} - You have".format(viewer)
    if len(args[2]) > 1:
        target = args[2][1].lower()
        if target[0] == '@':
            target = target[1:]
        start = "@{0} - @{1} has".format(viewer, target)

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    if not check_viewer_exists(target):
        if target == viewer:
            return "@{0} - It appears we just met. Hello! VoHiYo".format(viewer)
        else: return "@{0} - Cannot find that viewer.".format(viewer)

    currency = get_viewer_value(target, queue, 'currency')
    warnings = get_viewer_value(target, queue, 'warnings')
    created = get_viewer_value(target, queue, 'created')

    return "{0} {1} {2}{3}, {4} warning{5}, and I first met {6} in {7}! VoHiYo".format(
        start,
        '{:,}'.format(currency),
        currency_name,
        "s" if currency != 1 else "",
        warnings,
        "s" if warnings != 1 else "",
        "you" if target == viewer else "them",
        created
    )
