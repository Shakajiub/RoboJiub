from src.lib.functions_points import *

def shakadonate(viewer, args):
	#usage = '!shakadonate <user> <amount>'
	recipient = args[0].lower()

	if not check_viewer_exists(recipient):
		return "cannot find user!"

	if not args[1].isdigit():
		return "that's not an integer!"
	points_amount = int(args[1])

	if get_viewer_points_raw(viewer) < points_amount:
		return "you don't have enough points for that!"

	award_viewer(viewer, -points_amount)
	award_viewer(recipient, points_amount)

	return "donated %s points to %s!" % (points_amount, recipient)
