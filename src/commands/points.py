from src.config.config import get_config
from src.currency.currency import *

def points(args):
    """Get the amount of points the caller has."""
    #usage = "usage: s!points"

    # TODO - Get the points of another viewer ("s!points (viewer)")

    queue = args[0]
    viewer = args[1]

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    currency = get_viewer_value(viewer, queue, 'currency')
    return "@{0} - You have {1} {2}{3}!".format(viewer, currency, currency_name, "s" if currency != 1 else "")
