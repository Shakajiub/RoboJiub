global config

config = {

	# Details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'RoboJiub',
	'oauth_password': 'oauth:', # Get this from http://twitchapps.com/tmi/

	# Channels to join
	'channels': ['#shakajiub'],

	'cron': {
		'#shakajiub': {
			'run_cron': True,
			'run_time': 60,
			'cron_messages': [
				'I am here CoolCat'
			]
		}
	},

	# If set to true will display any data received
	'debug': False,

	# If set to true will log all messages from all channels
	'log_messages': True,

	# Maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 2048
}
