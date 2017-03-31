from src.config.config import get_config
from src.currency.currency import *

def donate(args):
    """Return a string explaining if the donation was succesful."""
    if len(args[1]) != 3:
        return False
    config = get_config()
    user_input = args[1]
    try:
        if not config['currency']['enabled']:
            return None
        if not user_input[2].isdigit():
            return False

        viewer = args[0]
        recipient = user_input[1].lower()
        if not check_viewer_exists(recipient):
            return "Cannot find donation target!"

        donation_amount = int(user_input[2])
        if donation_amount < 1:
            return "Minimum donation amount is 1!"

        currency_name = config['currency']['name']
        if get_viewer_value(viewer, 'currency') < donation_amount:
            return "You don't have enough {0}s for that!".format(currency_name)

        award_viewer(viewer, -donation_amount)
        award_viewer(recipient, donation_amount)
        plural = ""
        if donation_amount != 1:
            plural = "s"
        return "{0} donated {1} {2}{3} to {4}!".format(
            viewer, donation_amount, currency_name, plural, recipient
        )
    except KeyError:
        print("Currency config is corrupted!")
        return None
