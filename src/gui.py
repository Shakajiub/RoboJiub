try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk

import Queue
import tkFont

from time import localtime, strftime
from src.config.config import *

class RoboGUI:
	"""
	TODO description
	"""
	def __init__(self, master, queue, irc, end_app, toggle_bot):
		self.queue = queue
		self.irc = irc
		self.bg_color = 'BG_dark'

		#default_font = tkFont.nametofont("TkDefaultFont")
		#default_font.configure(family='Courier', size=10)

		# Set up the root widget
		master.wm_title("RoboJiub (testing version)")
		master.configure(background='#505050')
		master.resizable(width=False, height=False)

		# Chat and debug log
		self.log = tk.Text(master, width=80, height=20, background='#323232', foreground='#cccccc')
		self.log.configure(state='disabled') # This gets input only from code
		self.log.tag_configure('BG_dark', background='#323232')
		self.log.tag_configure('BG_light', background='#3c3c3c')
		self.log.tag_configure('BG_error', background='#460000')
		self.log.tag_configure('BG_success', background='#004600')
		self.log.tag_configure('BG_progress', background='#464600')
		self.log.pack(anchor=tk.W, padx=10, pady=10)

		# Button to quit the application
		button_end_app = tk.Button(master, text='Quit', command=end_app)
		button_end_app.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

		# Button to connect/disconnet the bot
		self.button_toggle_bot = tk.Button(master, text='Connect', command=toggle_bot)
		self.button_toggle_bot.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

		# Manual post button
		button_post = tk.Button(master, text='Post', command=self.manual_post)
		button_post.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

		# Manual post input widget
		self.manual_text_box = tk.Text(master, width=40, height=2, background='#323232', foreground='#cccccc')
		self.manual_text_box.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

	def toggle_bot_button(self, toggle):
		if toggle:
			self.button_toggle_bot.configure(text='Disconnect')
		else: self.button_toggle_bot.configure(text='Connect')

	def process_incoming(self):
		"""
		Handle all the messages currently in the queue (if any)
		"""
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				msg_text = msg[0]
				msg_color = msg[1]

				if msg_color == 'BG_chat':
					msg_color = self.bg_color
					if self.bg_color == 'BG_dark':
						self.bg_color = 'BG_light'
					else: self.bg_color = 'BG_dark'

				msg_time = strftime('%X', localtime()) + ' '

				self.log.configure(state='normal')
				self.log.insert(tk.END, msg_time + msg_text + '\n', msg_color)
				self.log.see(tk.END)
				self.log.configure(state='disabled')

			except Queue.Empty:
				pass

	def manual_post(self):
		config = get_config()
		log_msg = self.manual_text_box.get('1.0', tk.END).replace('\n', ' ')

		self.queue.put(('[robojiub]: %s' % log_msg, 'BG_chat'))
		self.irc.send_message(config['irc']['channel'], log_msg)
		self.manual_text_box.delete('1.0', tk.END)
