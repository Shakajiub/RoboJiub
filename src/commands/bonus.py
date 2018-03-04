from src.viewers.viewers import check_viewer_exists
from src.currency.currency import *

def bonus(args):
    """Award extra points to given viewer. Generally mod-only."""
    usage = "usage: s!bonus (recipient) (amount)"

    if len(args[2]) != 3:
        return usage

    queue = args[0]
    viewer = args[1]
    message = args[2]

    if message[2][0] == '-':
        if not message[2][1:].isdigit():
            return "@{0} - Invalid amount.".format(viewer)
    elif not message[2].isdigit():
        return "@{0} - Invalid amount.".format(viewer)

    recipient = message[1].lower()
    if recipient[0] == '@':
        recipient = recipient[1:]
    bonus_amount = int(message[2])

    if not check_viewer_exists(recipient):
        return "@{0} - Cannot find bonus target.".format(viewer)

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    award_viewer(recipient, bonus_amount, queue)
    if bonus_amount < 0:
        return "@{0} - Removed {1} {2}{3} from @{4}.".format(
            viewer, '{:,}'.format(bonus_amount), currency_name, "s" if bonus_amount != 1 else "", recipient
        )
    return "@{0} - Awarded {1} {2}{3} to @{4}!".format(
        viewer, '{:,}'.format(bonus_amount), currency_name, "s" if bonus_amount != 1 else "", recipient
    )
