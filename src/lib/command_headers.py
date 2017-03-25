from src.config.config import *

commands = {
	'!shakapoints': {
		'limit': 1,
		'argc': 0,
		'return': 'command'
	},

	'!shakagamble': {
		'limit': 1,
		'argc': 1,
		'return': 'command'
	},

	'!shakadonate': {
		'limit': 1,
		'argc': 2,
		'return': 'command'
	}
}

for channel in config['channels']:
	for command in commands:
		commands[command][channel] = {}
		commands[command][channel]['last_used'] = 0
