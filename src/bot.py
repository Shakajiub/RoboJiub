import os
import time
import Queue
import threading
import importlib

from src.irc import *
from src.gui import *
from src.commands import *
from src.config.config import *
from src.currency.currency import award_all_viewers

class RoboJiub:
    def __init__(self, root):
        """Instantiate our gui, irc, message queue and state booleans."""
        self.root = root
        self.queue = Queue.Queue()
        self.irc = IRC(self.queue)
        self.gui = RoboGUI(root, self.queue, self.irc, self.end_application, self.toggle_bot)

        self.running = True
        self.connected = False
        self.cron_value = 1 # Has to be high enough for cron messages
        self.currency_timer = time.time()
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
            self.socket = self.irc.get_socket_object()
            thread_main = threading.Thread(target=self.robo_main)
            thread_main.start()
        else:
            self.connected = False
            self.queue.put(("Disconnecting from the channel", 'BG_progress'))
            self.irc.end_connection()
        self.gui.toggle_bot_button(self.connected) # Forward connection status to the gui

    def load_crons(self):
        """Force-reload the config and load all cron messages."""
        config = get_config(True)
        self.crons = {}
        try:
            current_time = time.time()
            for cron in config['cron']:
                new_cron = config['cron'][cron]
                if new_cron['enabled']:
                    self.crons[cron] = {
                        'timer': current_time,
                        'timer_max': new_cron['timer'],
                        'message': new_cron['message']
                    }
        except KeyError:
            self.queue.put(("load_crons() - Cron config is corrupted", 'BG_error'))
            self.crons = {}

    def update_crons(self):
        """Update all cron messages, post them to chat when ready."""
        if self.cron_value < 1:
            return
        current_time = time.time()
        for cron in self.crons:
            loop_cron = self.crons[cron]
            if current_time - loop_cron['timer'] > loop_cron['timer_max']:
                loop_cron['timer'] = current_time
                botname = get_botname()
                self.cron_value = 0
                self.queue.put(("[{0}]: {1}".format(botname, loop_cron['message']), 'BG_chat'))
                self.irc.send_message(loop_cron['message'])

    def update_currency(self):
        """If the currency system is enabled, reward all viewers according to the config."""
        config = get_config()
        current_time = time.time()
        try:
            if config['currency']['enabled']:
                if current_time - self.currency_timer > config['currency']['timer']:
                    if config['currency']['log']:
                        self.queue.put(("Awarding currency to current viewers", 'BG_progress'))
                    self.currency_timer = current_time
                    thread_currency = threading.Thread(target=award_all_viewers,
                                args=(config['currency']['amount'], self.queue))
                    thread_currency.start()
        except KeyError:
            self.queue.put(("update_currency() - Currency config is corrupted", 'BG_error'))

    def after_loop(self):
        """Handle events outside of tkinter (puts itself after root loop 10 times per second)."""
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
        try:
            botname = config['irc']['username']
        except KeyError:
            botname = "botname"
            queue.put(("robo_main() - IRC config is corrupted", 'BG_error'))

        while self.connected:
            data = sock.recv(1024)
            if len(data) == 0:
                queue.put(("Connection was lost, reconnecting", 'BG_progress'))
                sock = self.irc.get_socket_object()

            irc.check_for_ping(data)
            if not irc.check_for_message(data):
                continue
            message_dict = irc.get_message(data)
            username = message_dict['username'].encode('utf-8')
            try:
                if username == config['irc']['username']:
                    continue
            except KeyError:
                queue.put(("robo_main() - IRC config is corrupted", 'BG_error'))
                continue
            message = message_dict['message'].encode('utf-8')
            log_msg = "[{0}]: {1}".format(username, message)
            queue.put((log_msg[:-1], 'BG_chat'))
            self.cron_value = 1

            if not message.startswith("s!"):
                if message.startswith("@{0}".format(botname)): # Replace @bot with s!question
                    message = "s!question {0}".format(message.split(' ', 1)[1])
                else:
                    continue
            command_name = message[2:-1].split(' ')[0]
            try:
                if not config['commands'][command_name]['enabled']:
                    queue.put(("Command '{0}' is disabled, ignoring request".format(
                                command_name), 'BG_progress'))
                    continue
                args = (queue, username, message[:-1].split(' '))
                module = importlib.import_module('src.commands.{0}'.format(command_name))
                result = getattr(module, command_name)(args)
                if result is None: # Commands return None if there was an error
                    continue
                if not result: # Commands return False if called incorrectly
                    result = "usage - {0}".format(config['commands'][command_name]['usage'])
                queue.put(("[{0}]: {1}".format(config['irc']['username'], result), 'BG_chat'))
                irc.send_message(result)

            except KeyError:
                queue.put(("Command '{0}' is not defined".format(command_name), 'BG_progress'))
            except ImportError:
                queue.put(("robo_main() - Could not import module '{0}'".format(
                            command_name), 'BG_error'))
            except AttributeError:
                queue.put(("robo_main() - No function found in module '{0}'".format(
                            command_name), 'BG_error'))
