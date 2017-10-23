from random import randrange

def roll(args):
    max_roll = 100

    if len(args[2]) > 1:
        try:
            max_roll = int(args[2][1])
        except ValueError:
            return "@{0} - That's not a valid number!".format(args[1])
        if max_roll < 2:
            return "@{0} - Minimum roll max is 2! (coin-flip)".format(args[1])

    return "@{0} - Rolled {1}! (out of {2})".format(args[1], randrange(1, max_roll), max_roll)
