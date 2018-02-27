from random import randrange
from src.viewers.viewers import *
from src.currency.currency import *

def gamble(args):
    """Gamble a given amount of points. 60 percent chance to lose, 40 to win."""
    usage = "usage: s!gamble (amount)"

    if len(args[2]) != 2:
        return usage

    queue = args[0]
    viewer = args[1]
    message = args[2]

    if not message[1].isdigit():
        return "@{0} - Invalid amount.".format(viewer)

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    viewer_points = get_viewer_value(viewer, queue, 'currency')
    gamble_amount = int(message[1])

    if viewer_points < gamble_amount:
        return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)

    random_roll = randrange(1, 100)

    if random_roll == 100:
        award_viewer(viewer, gamble_amount * 2, queue)
        return "@{0} - Rolled 100! Won {1} {2}s, you now have {3} {2}s!".format(
            viewer, '{:,}'.format(gamble_amount * 3), currency_name, '{:,}'.format(viewer_points + (gamble_amount * 2))
        )
    elif random_roll > 59:
        award_viewer(viewer, gamble_amount, queue)
        return "@{0} - Rolled {1}! Won {2} {3}s, you now have {4} {3}s!".format(
            viewer, random_roll, '{:,}'.format(gamble_amount * 2), currency_name, '{:,}'.format(viewer_points + gamble_amount)
        )
    else:
        award_viewer(viewer, -gamble_amount, queue)
        return "@{0} - Rolled {1}! Lost {2} {3}s, you now have {4} {3}s.".format(
            viewer, random_roll, '{:,}'.format(gamble_amount), currency_name, '{:,}'.format(viewer_points - gamble_amount)
        )
