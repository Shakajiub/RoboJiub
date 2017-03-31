from random import randrange

from src.config.config import get_config
from src.currency.currency import *

def gamble(args):
    """Return a string explaining if and how much currency the caller won/lost."""
    if len(args[1]) != 2:
        return False
    config = get_config()
    user_input = args[1]
    try:
        if not config['currency']['enabled']:
            return None
        if not user_input[1].isdigit():
            return False

        viewer = args[0]
        gamble_amount = int(user_input[1])
        viewer_points = get_viewer_value(viewer, 'currency')
        currency_name = config['currency']['name']

        if viewer_points < gamble_amount:
            return "You don't have enough {0}s for that!".format(currency_name)

        random_roll = randrange(1, 100)
        if random_roll == 100:
            award_viewer(viewer, gamble_amount * 2)
            return "{0} rolled 100! Won {1} {2}s, now has {3} {2}s!".format(
                viewer, gamble_amount * 3, currency_name,
                viewer_points + (gamble_amount * 2)
            )
        elif random_roll > 59:
            award_viewer(viewer, gamble_amount)
            return "{0} rolled {1}! Won {2} {3}s, now has {4} {3}s!".format(
                viewer, random_roll, gamble_amount * 2, currency_name,
                viewer_points + gamble_amount
            )
        else:
            award_viewer(viewer, -gamble_amount)
            return "{0} rolled {1}! Lost {2} {3}s, now has {4} {3}s.".format(
                viewer, random_roll, gamble_amount, currency_name,
                viewer_points - gamble_amount
            )
    except KeyError:
        print("Currency config is corrupted!")
        return None
