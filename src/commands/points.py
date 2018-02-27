from src.config import get_config
from src.viewers.viewers import *
from src.currency.currency import *

def points(args):
    """Get the amount of points a viewer has."""
    #usage = "usage: s!points (viewer)"

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
        return "@{0} - Cannot find that viewer.".format(viewer)

    currency = get_viewer_value(target, queue, 'currency')
    return "{0} {1} {2}{3}!".format(start, '{:,}'.format(currency), currency_name, "s" if currency != 1 else "")
