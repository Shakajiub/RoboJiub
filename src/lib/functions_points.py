import os
import json
from urllib2 import urlopen
from src.config.config import *

# Check if the given viewer exists
def check_viewer_exists(viewer):
	path = "./viewers/" + viewer + ".txt"
	return os.path.isfile(path)

# Create a fresh viewer file
def create_viewer(viewer):
	f = open("./viewers/" + viewer + ".txt", "w+")
	f.write("10")
	f.close()

# Award a viewer with some points
def award_viewer(viewer, amount):
	if not check_viewer_exists(viewer):
		create_viewer(viewer)

	points = ''
	f = open("./viewers/" + viewer + ".txt", "r")
	if f.mode == 'r':
		points = f.read()
		f.close()

	points.strip()
	f = open("./viewers/" + viewer + ".txt", "w+")
	f.write(str(int(points) + amount))
	f.close()

# Award all viewers with some points
def award_all_viewers(amount):
	for channel in config['channels']:
		channel = channel.replace('#','')
		
		response = urlopen('http://tmi.twitch.tv/group/user/%s/chatters' % channel)
		parsed_json = json.loads(response.read())

		for category in parsed_json['chatters']:
			#print("\r\n" + category + ":")
			for viewer in parsed_json['chatters'][category]:
				#print(viewer)
				award_viewer(viewer, amount)
				#print("awarding " + viewer)

# Get the amount of points a viewer has
def get_viewer_points(viewer):
	if not check_viewer_exists(viewer):
		create_viewer(viewer)

	f = open("./viewers/" + viewer + ".txt", "r")
	if f.mode == 'r':
		contents = f.read()
		f.close()
		return "has " + contents + " points!"
	else: return "has broken the bot!"

# Get the raw integer amount of points a viewer has
def get_viewer_points_raw(viewer):
	if not check_viewer_exists(viewer):
		create_viewer(viewer)

	f = open("./viewers/" + viewer + ".txt", "r")
	if f.mode == 'r':
		contents = f.read()
		f.close()
		return int(contents)
	else: return 0
