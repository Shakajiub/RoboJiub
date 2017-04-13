from src.config.config import get_config
from src.currency.currency import *

def donate(args):
    """Return a string explaining if the donation was succesful."""
    if len(args[2]) != 3:
        return False
    queue = args[0]
    config = get_config()
    user_input = args[2]

    try:
        if not config['currency']['enabled']:
            return None
        if not user_input[2].isdigit():
            return False
        currency_name = config['currency']['name']
    except KeyError:
        queue.put(("donate() - Currency config is corrupted", 'BG_error'))
        return None

    viewer = args[1]
    recipient = user_input[1].lower()
    if not check_viewer_exists(recipient):
        return "@{0} - Cannot find donation target!".format(viewer)

    donation_amount = int(user_input[2])
    if donation_amount < 1:
        return "@{0} - Minimum donation amount is 1!".format(viewer)

    if get_viewer_value(viewer, queue, 'currency') < donation_amount:
        return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)

    award_viewer(viewer, -donation_amount, queue)
    award_viewer(recipient, donation_amount, queue)
    return "@{0} donated {1} {2}{3} to @{4}!".format(
        viewer, donation_amount, currency_name, "s" if donation_amount != 1 else "", recipient
    )
