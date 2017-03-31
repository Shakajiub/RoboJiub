from src.config.config import get_config
from src.currency.currency import get_viewer_value

def points(args):
    """Return a string explaining how much currency the caller has."""
    if len(args[3]) > 1:
        return False
    config = get_config()
    try:
        viewer = args[2]
        currency_name = config['currency']['name']
        currency = get_viewer_value(viewer, 'currency')
        plural = ""
        if currency != 1:
            plural = "s"
        return "{0} has {1} {2}{3}!".format(viewer, currency, currency_name, plural)
    except KeyError:
        print("Currency config is missing key 'name'!")
        return None
