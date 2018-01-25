from src.currency.currency import get_mods, award_viewer

global bets
bets = None

def bet(args):
    """Allow viewers to bet on anything, award points to closest guess."""
    usage = "usage: s!bet (amount)/check"
    global bets

    if len(args[2]) < 2:
        return None

    viewer = args[1]
    message = args[2]

    # Moderators will manage the flow of the bet with these commands:
    # s!bet start : starts the betting system
    # s!bet close : closes the bets, no new bets will be accepted
    # s!bet end (score) : ends the bet, closest better to (score) wins

    if message[1] in ["start", "close", "end"]:
        if viewer not in get_mods():
            return None

        if message[1][0] == 's':
            return start_bet()
        elif message[1][0] == 'e':
            return end_bet(message, args[0])

        elif bets != None:
            bets['closed'] = True
            return "The bets have been closed! No new bets will be accepted!"
        else: return None

    # "bets" is None when there is no bet running, otherwise it's a dictionary of viewer bets
    elif bets == None:
        return None

    # Using "s!bet check" people can check their bets
    elif message[1] == "check":
        if viewer in bets:
            return "@{0} - Your bet is {1}.".format(viewer, bets[viewer])
        else: return "@{0} - You have not bet anything yet.".format(viewer)

    # An imaginary viewer "closed" controls whether or not new bets are accepted
    elif bets['closed']:
        return "@{0} - The bets have been closed! Wait for the next game.".format(viewer)

    elif not message[1].isdigit():
        return "@{0} - Invalid amount.".format(viewer)

    # If all is good, accept a new bet from a viewer
    elif viewer not in bets:
        bets[viewer] = int(message[1])
        return "@{0} - Bet registered!".format(viewer)
    else: return "@{0} - You have already bet!".format(viewer)

def start_bet():
    global bets
    if bets != None:
        return "A bet is already running!"

    bets = { 'closed': False }
    return 'A bet has started! Set your bets with "s!bet (score)" PogChamp'

def end_bet(message, queue):
    global bets
    if len(message) != 3 or bets == None:
        return None

    score = message[2]
    if not score.isdigit():
        return None

    if len(bets) == 1:
        bets = None
        return "The bet has ended! No winners!"

    bets.pop('closed', 0)
    key, value = min(bets.items(), key=lambda(_, v): abs(v - int(score)))
    bets = None

    award_viewer(key, 100, queue)
    return "The bet has ended! The winner is @{0}! You won 100 points!".format(key)
