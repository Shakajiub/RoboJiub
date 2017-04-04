from src.config.config import get_config
from src.currency.currency import get_viewer_value

def points(args):
    """Return a string explaining how much currency the caller has."""
    if len(args[2]) > 1:
        return False
    config = get_config()
    queue = args[0]
    try:
        if not config['currency']['enabled']:
            return None
        viewer = args[1]
        currency_name = config['currency']['name']
        currency = get_viewer_value(viewer, queue, 'currency')
        plural = ""
        if currency != 1:
            plural = "s"
        return "@{0} - You have {1} {2}{3}!".format(viewer, currency, currency_name, plural)
    except KeyError:
        queue.put(("points() - Currency config is corrupted", 'BG_error'))
        return None
