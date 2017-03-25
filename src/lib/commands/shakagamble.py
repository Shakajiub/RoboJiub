import random
from src.lib.functions_points import *

def shakagamble(viewer, args):
	usage = '!shakagamble <points>'

	if not args[0].isdigit():
		return "that's not an integer!"

	gamble_amount = int(args[0])
	viewer_points = get_viewer_points_raw(viewer)

	if viewer_points < gamble_amount:
		return "you don't have enough points for that!"

	# <3
	if viewer == 'papercat84':
		award_viewer(viewer, -gamble_amount)
		return 'rolled %s, lost %s points!' % (random.randrange(1, 59), gamble_amount)

	random_roll = random.randrange(1, 100)
	if random_roll > 59:
		award_viewer(viewer, gamble_amount)
		return 'rolled %s, won %s points, now has %s points!' % (random_roll, gamble_amount * 2, viewer_points + gamble_amount)
	else:
		award_viewer(viewer, -gamble_amount)
		return 'rolled %s, lost %s points, now has %s points!' % (random_roll, gamble_amount, viewer_points - gamble_amount)
