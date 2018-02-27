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

    if not message[2].isdigit():
        return "@{0} - Invalid amount.".format(viewer)

    recipient = message[1].lower()
    donation_amount = int(message[2])

    if not check_viewer_exists(recipient):
        return "@{0} - Cannot find bonus target.".format(viewer)

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    award_viewer(recipient, donation_amount, queue)
    return "@{0} - Awarded {1} {2}{3} to @{4}!".format(
        viewer, '{:,}'.format(donation_amount), currency_name, "s" if donation_amount != 1 else "", recipient
    )
