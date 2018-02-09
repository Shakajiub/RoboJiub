from src.currency.currency import *

def donate(args):
    """Move points from one viewer (caller) to another."""
    usage = "usage: s!donate (recipient) (amount)"

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
        return "@{0} - Cannot find donation target.".format(viewer)

    if donation_amount < 1:
        return "@{0} - Minimum donation amount is 1!".format(viewer)

    currency_name = get_currency(queue)
    if not currency_name:
        return None # None is returned on internal errors

    if get_viewer_value(viewer, queue, 'currency') < donation_amount:
        return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)

    award_viewer(viewer, -donation_amount, queue)
    award_viewer(recipient, donation_amount, queue)
    return "@{0} - Donated {1} {2}{3} to @{4}!".format(
        viewer, '{:,}'.format(donation_amount), currency_name, "s" if donation_amount != 1 else "", recipient
    )
