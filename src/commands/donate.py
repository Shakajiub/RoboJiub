from src.currency.currency import *

def donate(args):
    """Return a string explaining if the donation was succesful."""
    if len(args[2]) != 3:
        return False
    queue = args[0]
    user_input = args[2]

    currency_name = validate_currency(user_input[2], queue)
    if not currency_name:
        return currency_name

    viewer = args[1]
    recipient = user_input[1].lower()
    if not check_viewer_exists(recipient):
        return "@{0} - Cannot find donation target!".format(viewer)

    donation_amount = int(user_input[2])
    if donation_amount < 1:
        return "@{0} - Minimum donation amount is 1!".format(viewer)

    if get_viewer_value(viewer, queue, 'currency') < donation_amount:
        return "@{0} - You don't have enough {1}s for that!".format(viewer, currency_name)

    award_viewer(viewer, -donation_amount, queue)
    award_viewer(recipient, donation_amount, queue)
    return "@{0} donated {1} {2}{3} to @{4}!".format(
        viewer, donation_amount, currency_name, "s" if donation_amount != 1 else "", recipient
    )
