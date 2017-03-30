# TODO better requirements for cron messages (chat inactivity, message amount, ...)
# TODO a better way to exit while waiting for socket.recv() - (after_loop())

import os
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
        self.gui = RoboGUI(master, self.queue, self.irc, self.end_application, self.toggle_bot)

        self.running = 1
        self.connected = 0
        self.cron_value = 1 # Has to be high enough for cron messages

        self.after_loop()

    def end_application(self):
        """
        Toggle flags to disconnect the irc socket and close the GUI
        """
        self.connected = 0
        self.running = 0

    def toggle_bot(self):
        """
        Connect/disconnect the irc socket
        """
        if not self.connected:
            self.load_crons()
            self.connected = 1
            self.socket = self.irc.get_irc_socket_object()
            thread_main = threading.Thread(target=self.robo_main)
            thread_main.start()
        else:
            self.connected = 0
            self.queue.put(('Disconnecting from the channel ...', 'BG_progress'))
            self.irc.end_connection()

        self.gui.toggle_bot_button(self.connected) # Forward connection status to Tkinter GUI

    def load_crons(self):
        """
        Load all cron messages from the config
        """
        config = get_config(True)
        self.crons = {}

        for cron in config["cron"]:
            new_cron = config["cron"][cron]
            if new_cron["enabled"]:
                self.crons[cron] = [new_cron["timer"] * 10, 0]

    def update_crons(self):
        """
        Update all cron messages, post them to chat when ready
        """
        for cron in self.crons:
            cron_timer = self.crons[cron]
            cron_timer[1] += 1

            if (cron_timer[1] >= cron_timer[0]):
                cron_timer[1] = 0
                cron_message = get_config()["cron"][cron]["message"]

                self.cron_value = 0
                self.queue.put((cron_message, 'BG_chat'))
                self.irc.send_message(cron_message)

    def after_loop(self):
        """
        Handle events outside of Tkinter (called 10 times per second)
        """
        self.gui.handle_queue()

        if not self.running:
            self.master.destroy()
            pid = os.getpid()
            os.kill(pid, 9)

        elif self.connected and self.cron_value > 0:
            self.update_crons()

        self.master.after(100, self.after_loop)

    def robo_main(self):
        """
        Handle messages received via irc socket (main function of the bot, basically)
        """
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

            if not irc.check_for_message(data):
                continue

            message_dict = irc.get_message(data)
            username = message_dict['username']

            if username == config['irc']['username']:
                continue

            message = message_dict['message']
            log_msg = '[%s]: %s' % (username, message)
            queue.put((log_msg[:-1], 'BG_chat'))

            self.cron_value = 1

            if message[0] == '!':
                command_name = message.replace('!', '')[:-1].split(' ')[0]
                try:
                    if not config["commands"][command_name]["enabled"]:
                        print 'User tried to call disabled command: %s' % command_name
                        continue

                    args = (irc, queue, message.split(' '))
                    module = importlib.import_module('src.commands.%s' % command_name)
                    result = getattr(module, command_name)(args)

                    if not result:
                        result = 'Usage: %s' % config["commands"][command_name]["usage"]

                    queue.put(('[%s]: %s' % (config["irc"]["username"], result), 'BG_chat'))
                    irc.send_message(result)

                except KeyError:
                    print 'Command not defined in config json: %s' % command_name
                except ImportError:
                    print 'Could not import module: %s' % command_name
                except AttributeError:
                    print 'No proper method found in module: %s' % command_name
