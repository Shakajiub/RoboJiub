try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import Queue
import tkFont

from time import localtime, strftime
from src.config import *

class RoboGUI:
    def __init__(self, root, queue, irc, end_app, toggle_bot):
        """Setup everything for our tkinter gui."""
        self.queue = queue
        self.irc = irc
        self.bg_color = 'BG_dark'

        # Set up the root widget
        root.wm_title("RoboJiub (testing version)")
        root.configure(background='#505050')
        root.resizable(width=False, height=False)

        # Chat log
        self.log = tk.Text(root, width=80, height=20, background='#323232', foreground='#cccccc')
        self.log.configure(state='disabled') # Get input only from code
        self.log.tag_configure('BG_dark', background='#323232')
        self.log.tag_configure('BG_light', background='#3c3c3c')
        self.log.tag_configure('BG_whisper', background='#282828')
        self.log.tag_configure('BG_error', background='#460000')
        self.log.tag_configure('BG_success', background='#004600')
        self.log.tag_configure('BG_progress', background='#464600')
        self.log.tag_configure('FG_notice', foreground='#999999')
        self.log.tag_configure('FG_mod', foreground='#00d2d2')
        self.log.tag_configure('FG_sub', foreground='#d200d2')
        self.log.pack(anchor=tk.W, padx=10, pady=10)

        # Button to quit the application
        button_end_app = tk.Button(root, text="Quit", command=end_app)
        button_end_app.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

        # Button to connect/disconnect the bot
        self.button_toggle_bot = tk.Button(root, text="Connect", command=toggle_bot)
        self.button_toggle_bot.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

        # Manual post button
        button_post = tk.Button(root, text="Post", command=self.manual_post)
        button_post.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

        # Manual post input widget
        self.manual_text_box = tk.Text(root, width=40, height=2)
        self.manual_text_box.configure(background='#323232', foreground='#cccccc')
        self.manual_text_box.pack(anchor=tk.W, side=tk.LEFT, padx=10, pady=10)

    def toggle_bot_button(self, toggle):
        """Toggle the text on the connection button (Connect/Disconnect)."""
        if toggle:
            self.button_toggle_bot.configure(text="Disconnect")
        else:
            self.button_toggle_bot.configure(text="Connect")

    def prepare_queue_message(self, msg_text, msg_color):
        """Return the proper color and suffix for given message."""
        if msg_color == 'BG_chat':
            msg_color = self.bg_color
            if self.bg_color == 'BG_dark':
                self.bg_color = 'BG_light'
            else: self.bg_color = 'BG_dark'

        elif msg_color == 'BG_error':
            msg_text = "ERROR: " + msg_text
            print(msg_text)

        return msg_text, msg_color

    def handle_queue(self):
        """Handle messages currently in the queue (print them, if any)."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                msg_text, msg_color = self.prepare_queue_message(msg[0], msg[1])
                msg_time = strftime("%X ", localtime())
                self.log.configure(state='normal')

                if len(msg) == 6: # Chat messages have a bunch of user information:
                    # msg[0] == The message itself
                    # msg[1] == Background color tag (generally 'BG_chat')
                    # msg[2] == Username of the message's poster
                    # msg[3] == Custom color for the username
                    # msg[4] == '1' if the user is a moderator, otherwise '0'
                    # msg[5] == '1' if the user is a subscriber, otherwise '0'

                    self.log.tag_configure(msg[2], foreground=msg[3])
                    self.log.insert(tk.END, msg_time, msg_color)
                    self.log.insert(tk.END, "[{0}]".format(msg[2]), (msg_color, msg[2]))
                    if msg[4] == '1': self.log.insert(tk.END, "[M]", (msg_color, 'FG_mod'))
                    if msg[5] == '1': self.log.insert(tk.END, "[S]", (msg_color, 'FG_sub'))
                    self.log.insert(tk.END, ": " + msg_text + '\n', msg_color)

                else: # Other messages to print are simpler (generally debug & error messages):
                    self.log.insert(tk.END, msg_time + msg_text + '\n', msg_color)

                self.log.see(tk.END)
                self.log.configure(state='disabled')
            except Queue.Empty: pass

    def manual_post(self):
        """Post a custom message as the bot (and clear the input text box)."""
        log_msg = self.manual_text_box.get('1.0', tk.END).replace('\n', ' ')
        if len(log_msg.strip(' ')) > 0:
            self.queue.put(("[{0}]: {1}".format(get_botname(), log_msg), 'BG_chat'))
            self.irc.send_message(log_msg)
        self.manual_text_box.delete('1.0', tk.END)
