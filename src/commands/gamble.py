from random import randrange

from src.config.config import get_config
from src.currency.currency import *

def gamble(args):
    """Return a string explaining if and how much currency the caller won/lost."""
    if len(args[2]) != 2:
        return False
    queue = args[0]
    try:
        config = get_config()
        user_input = args[2]

        if not config['currency']['enabled']:
            return None
        if not user_input[1].isdigit():
            return False

        viewer = args[1]
        gamble_amount = int(user_input[1])
        viewer_points = get_viewer_value(viewer, queue, 'currency')
        currency_name = config['currency']['name']

        if viewer_points < gamble_amount:
            return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)

        random_roll = randrange(1, 100)
        if random_roll == 100:
            award_viewer(viewer, gamble_amount * 2, queue)
            return "@{0} - Rolled 100! Won {1} {2}s, you now have {3} {2}s!".format(
                viewer, gamble_amount * 3, currency_name,
                viewer_points + (gamble_amount * 2)
            )
        elif random_roll > 59:
            award_viewer(viewer, gamble_amount, queue)
            return "@{0} - Rolled {1}! Won {2} {3}s, you now have {4} {3}s!".format(
                viewer, random_roll, gamble_amount * 2, currency_name,
                viewer_points + gamble_amount
            )
        else:
            award_viewer(viewer, -gamble_amount, queue)
            return "@{0} - Rolled {1}! Lost {2} {3}s, you now have {4} {3}s.".format(
                viewer, random_roll, gamble_amount, currency_name,
                viewer_points - gamble_amount
            )
    except KeyError:
        queue.put(("gamble() - Currency config is corrupted", 'BG_error'))
        return None
