from random import randrange
from src.currency.currency import *

def gamble(args):
    """Return a string explaining if and how much currency the caller won/lost."""
    if len(args[2]) != 2:
        return False
    queue = args[0]
    user_input = args[2]

    currency_name = validate_currency(user_input[1], queue)
    if not currency_name:
        return currency_name

    viewer = args[1]
    viewer_points = get_viewer_value(viewer, queue, 'currency')
    gamble_amount = int(user_input[1])

    if viewer_points < gamble_amount:
        return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)
    return randomize_award(queue, viewer, viewer_points, gamble_amount, currency_name)

def randomize_award(queue, viewer, viewer_points, gamble_amount, currency_name):
    """Randomize the gamble reward and return the main reward string for the viewer."""
    random_roll = randrange(1, 100)

    if random_roll == 100:
        award_viewer(viewer, gamble_amount * 2, queue)
        return "@{0} - Rolled 100! Won {1} {2}s, you now have {3} {2}s!".format(
            viewer, gamble_amount * 3, currency_name, viewer_points + (gamble_amount * 2)
        )
    elif random_roll > 59:
        award_viewer(viewer, gamble_amount, queue)
        return "@{0} - Rolled {1}! Won {2} {3}s, you now have {4} {3}s!".format(
            viewer, random_roll, gamble_amount * 2, currency_name, viewer_points + gamble_amount
        )
    else:
        award_viewer(viewer, -gamble_amount, queue)
        return "@{0} - Rolled {1}! Lost {2} {3}s, you now have {4} {3}s.".format(
            viewer, random_roll, gamble_amount, currency_name, viewer_points - gamble_amount
        )
