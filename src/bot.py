# TODO better requirements for cron messages (chat inactivity, message amount, ...)
# TODO a better way to exit while waiting for socket.recv() - (in after_loop())
# TODO custom command time-limits
# TODO moderator-only commands (bonus, bonusall)
# TODO automoderator features
# TODO giveaway system
# TODO song request system
# TODO smart clever-bot style (heavily simplified) question system
# TODO more accurate cron system (use time instead of silly loop count)

import os
import Queue
import threading
import importlib

from src.irc import *
from src.gui import *
from src.commands import *
from src.config.config import get_config
from src.currency.currency import award_all_viewers

class RoboJiub:
    """
    TODO docstring.
    """
    def __init__(self, root):
        """Instantiate our gui, irc, message queue and state booleans."""
        self.root = root
        self.queue = Queue.Queue()
        self.irc = IRC(self.queue)
        self.gui = RoboGUI(root, self.queue, self.irc, self.end_application, self.toggle_bot)

        self.running = True
        self.connected = False
        self.cron_value = 1 # Has to be high enough for cron messages
        self.currency_timer = 100
        self.after_loop()

    def end_application(self):
        """Toggle flags to disconnect the irc socket and close the gui."""
        self.connected = False
        self.running = False

    def toggle_bot(self):
        """Connect/disconnect the irc socket."""
        if not self.connected:
            self.load_crons()
            self.connected = True
            self.socket = self.irc.get_irc_socket_object()
            thread_main = threading.Thread(target=self.robo_main)
            thread_main.start()
        else:
            self.connected = False
            self.queue.put(("Disconnecting from the channel ...", 'BG_progress'))
            self.irc.end_connection()
        self.gui.toggle_bot_button(self.connected) # Forward connection status to the gui

    def load_crons(self):
        """Force-reload the config and load all cron messages."""
        config = get_config(True)
        self.crons = {}
        try:
            for cron in config['cron']:
                new_cron = config['cron'][cron]
                if new_cron['enabled']:
                    self.crons[cron] = {
                        'timer': 0,
                        'timer_max': new_cron['timer'] * 10,
                        'message': new_cron['message']
                    }
        except KeyError:
            print("Cron message config is corrupted!")
            self.crons = {}

    def update_crons(self):
        """Update all cron messages, post them to chat when ready."""
        if self.cron_value < 1:
            return
        for cron in self.crons:
            loop_cron = self.crons[cron]
            loop_cron['timer'] += 1

            if loop_cron['timer'] >= loop_cron['timer_max']:
                config = get_config()
                loop_cron['timer'] = 0
                botname = config['irc']['username']
                self.cron_value = 0
                self.queue.put(("[{0}]: {1}".format(botname, loop_cron['message']), 'BG_chat'))
                self.irc.send_message(loop_cron['message'])

    def update_currency(self):
        """If the currency system is enabled, reward all viewers according to the config."""
        config = get_config()
        if self.currency_timer < 1:
            try:
                if config['currency']['enabled']:
                    if config['currency']['log']:
                        self.queue.put(("Awarding currency to current viewers ...", 'BG_progress'))
                    self.currency_timer = config['currency']['timer'] * 10
                    award_all_viewers(config['currency']['amount'])
            except KeyError:
                print("Currency config is corrupted!")
        else: self.currency_timer -= 1

    def after_loop(self):
        """Handle events outside of tkinter (recursive, looped 10 times per second)."""
        self.gui.handle_queue()

        if not self.running:
            self.root.destroy()
            pid = os.getpid()
            os.kill(pid, 9)
        elif self.connected:
            self.update_crons()
            self.update_currency()

        self.root.after(100, self.after_loop)

    def robo_main(self):
        """Handle messages received via irc socket (main function of the bot, basically)."""
        config = get_config()
        irc = self.irc
        sock = self.socket
        queue = self.queue

        while self.connected:
            data = sock.recv(1024)
            if len(data) == 0:
                queue.put(("Connection was lost, reconnecting ...", 'BG_progress'))
                sock = self.irc.get_irc_socket_object()

            irc.check_for_ping(data)
            if not irc.check_for_message(data):
                continue
            message_dict = irc.get_message(data)
            username = message_dict['username'].encode('utf-8')
            if username == config['irc']['username']:
                continue

            message = message_dict['message'].encode('utf-8')
            log_msg = "[{0}]: {1}".format(username, message)
            queue.put((log_msg[:-1], 'BG_chat'))
            self.cron_value = 1

            if message[0] == '!':
                command_name = message.replace('!', '')[:-1].split(' ')[0]
                try:
                    if not config['commands'][command_name]['enabled']:
                        print("User tried to call disabled command: {0}".format(command_name))
                        continue
                    args = (username, message[:-1].split(' '))
                    module = importlib.import_module('src.commands.{0}'.format(command_name))
                    result = getattr(module, command_name)(args)
                    if result is None: # Commands return None if there was an error
                        continue
                    if not result: # Commands return False if called incorrectly
                        result = "Usage: {0}".format(config['commands'][command_name]['usage'])
                    queue.put(("[{0}]: {1}".format(config['irc']['username'], result), 'BG_chat'))
                    irc.send_message(result)

                except KeyError:
                    print("Command not defined in config json: {0}".format(command_name))
                except ImportError:
                    print("Could not import module: {0}".format(command_name))
                except AttributeError:
                    print("No proper method found in module: {0}".format(command_name))
