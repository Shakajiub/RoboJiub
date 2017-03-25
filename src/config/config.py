global config

config = {

	# details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'RoboJiub',
	'oauth_password': 'oauth:', # get this from http://twitchapps.com/tmi/

	# channel to join
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

	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# todo
	'log_messages': True,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 2048
}
