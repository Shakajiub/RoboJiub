import Queue
import threading
import importlib

from src.irc import *
from src.gui import *
from src.commands import *
from src.config.config import *

class RoboJiub:
	"""
	TODO description
	"""
	def __init__(self, master):
		self.master = master
		self.queue = Queue.Queue()

		self.irc = IRC(self.queue)
		self.socket = None
		self.thread_main = None
		self.gui = RoboGUI(master, self.queue, self.irc, self.end_application, self.toggle_bot)

		self.running = 1
		self.connected = 0

		self.periodic_loop()

	def toggle_bot(self):
		if not self.connected:
			self.connected = 1
			self.socket = self.irc.get_irc_socket_object()
			self.thread_main = threading.Thread(target=self.robo_main)
			self.thread_main.start()
		else:
			self.connected = 0
			self.queue.put(('Disconnecting from the channel ...', 'BG_progress'))
			self.irc.end_connection()

		self.gui.toggle_bot_button(self.connected)

	def periodic_loop(self):
		"""
		Check if there is anything new in the queue
		"""
		self.gui.process_incoming()
		if not self.running:
			self.master.destroy()

			import os
			pid = os.getpid() # TODO figure out a better way to exit
			os.kill(pid, 9)   # while waiting for the socket.recv()

		self.master.after(100, self.periodic_loop)

	def end_application(self):
		self.connected = 0
		self.running = 0

	def robo_main(self):
		config = get_config()

		irc = self.irc
		sock = self.socket
		queue = self.queue

		while self.connected:
			data = sock.recv(1024)

			if len(data) == 0:
				queue.put(('Connection was lost, reconnecting ...', 'BG_progress'))
				sock = self.irc.get_irc_socket_object()

			irc.check_for_ping(data)

			if (irc.check_for_message(data)):
				message_dict = irc.get_message(data)

				#channel = message_dict['channel']
				message = message_dict['message']
				username = message_dict['username']

				if username != config['irc']['username'].lower():
					log_msg = '[%s]: %s' % (username, message)
					queue.put((log_msg[:-1], 'BG_chat'))

					if message[0] == '!':
						try:
							command_name = message.replace('!', '')[:-1].split(' ')[0]
							args = (irc, queue, message.split(' '))

							if (config["commands"][command_name]["enable"]):
								module = importlib.import_module('src.commands.%s' % command_name)
								result = getattr(module, command_name)(args)

								if not result:
									result = 'Usage: %s' % config["commands"][command_name]["usage"]

								queue.put(('[robojiub]: %s' % result, 'BG_chat'))
								irc.send_message(result)

							else: print 'User tried to call disabled command: %s' % command_name

						except ImportError:
							print 'Could not import module: %s' % command_name

						except AttributeError:
							print 'No proper method found in module: %s' % command_name

						except KeyError:
							print 'Command not defined in config json: %s' % command_name
