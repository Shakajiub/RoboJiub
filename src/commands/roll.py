from random import randrange

def roll(args):
    """Roll for a number between 1 and 100, or optionally given maximum."""
    #usage = "usage: s!roll (max)

    max_roll = 100

    if len(args[2]) > 1:
        try:
            max_roll = int(args[2][1])
        except ValueError:
            return "@{0} - Invalid amount.".format(args[1])
        if max_roll < 2:
            return "@{0} - Minimum roll max is 2!".format(args[1])

    return "@{0} - Rolled {1}! (d{2})".format(args[1], randrange(1, max_roll), max_roll)
