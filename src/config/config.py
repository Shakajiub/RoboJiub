import json

global config
config = None

def get_config():
	global config

	if config == None:
		with open('config.json') as config_file:
			config = json.load(config_file)

	return config
