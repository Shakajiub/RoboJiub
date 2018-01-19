from src.currency.currency import *

def bonus(args):
    """Return a string explaining if the bonus was successful."""
    if len(args[2]) != 3:
        return False
    queue = args[0]
    user_input = args[2]

    currency_name = validate_currency(user_input[2], queue)
    if not currency_name: # This can be False or None
        return currency_name

    viewer = args[1]
    recipient = user_input[1].lower()

    try:
        donation_amount = int(user_input[2])
    except ValueError:
        return "@{0} - That's not a valid number!".format(viewer)

    if not check_viewer_exists(recipient):
        return "@{0} - Cannot find donation target!"

    award_viewer(recipient, donation_amount, queue)
    return "@{0} - Awarded {1} {2}{3} to @{4}!".format(
        viewer, donation_amount, currency_name, "s" if donation_amount != 1 else "", recipient
    )
