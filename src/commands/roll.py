from random import randrange

def roll(args):
    max_roll = 100

    if len(args[2]) > 1:
        max_roll = int(args[2][1])

    return "@{0} - Rolled {1}!".format(args[1], randrange(1, max_roll))
