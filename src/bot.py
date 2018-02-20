import os
import time
import Queue
import threading
import importlib

from src.irc import *
from src.gui import *
from src.commands import *
from src.config.config import *
from src.currency.currency import get_mods, add_mod, award_all_viewers

class RoboJiub:
    def __init__(self, root):
        """Instantiate our gui, irc, message queue and state booleans."""
        self.root = root
        self.queue = Queue.Queue()
        self.irc = IRC(self.queue)
        self.gui = RoboGUI(root, self.queue, self.irc, self.end_application, self.toggle_bot)

        self.botname = None
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
            self.queue.put(("Disconnecting from the channel ...", 'BG_progress'))
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
            self.queue.put(("load_crons() - Cron config is corrupted!", 'BG_error'))
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
                if self.botname == None:
                    self.botname = get_botname().encode('utf-8').lower()
                self.cron_value = 0
                self.queue.put(("[{0}]: {1}".format(self.botname, loop_cron['message']), 'BG_chat'))
                self.irc.send_message(loop_cron['message'])

    def update_currency(self):
        """If the currency system is enabled, reward all viewers according to the config."""
        config = get_config()
        current_time = time.time()
        try:
            if config['currency']['enabled'] and current_time - self.currency_timer > config['currency']['timer']:
                if config['currency']['log']:
                    self.queue.put(("Awarding currency to current viewers ...", 'BG_progress'))
                self.currency_timer = current_time
                thread = threading.Thread(target=award_all_viewers, args=(config['currency']['amount'], self.queue))
                thread.start()
        except KeyError:
            self.queue.put(("update_currency() - Currency config is corrupted!", 'BG_error'))

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
        """Handle messages received via irc socket (main loop of the bot, basically)."""
        config = get_config()

        irc = self.irc
        sock = self.socket
        queue = self.queue

        while self.connected:
            data = sock.recv(1024)
            if len(data) == 0:
                queue.put(("Connection was lost, reconnecting ...", 'BG_progress'))
                sock = self.irc.get_socket_object()

            irc.check_for_ping(data)
            parsed_data = self.parse_socket_data(irc, data, queue)
            if parsed_data == None: continue

            username = parsed_data[0]
            message = parsed_data[1]
            command = parsed_data[2]

            if self.check_command_enabled(command, queue) == False:
                message = "s!custom {0}".format(message[2:])
                command = "custom"

            args = (queue, username, message.split(' '))
            module = self.get_command_module(command, queue)
            result = self.get_command_result(module, command, args)
            irc.send_message(result)

    def parse_socket_data(self, irc, data, queue):
        """Parse any received data from the socket and determine what to do with it."""
        msg_data = irc.check_for_message(data, queue)
        if not msg_data:
            return None

        # Notices are short messages that are sent when slowmode or follower/sub-only chat is toggled
        if msg_data['type'] == "NOTICE":
            queue.put((msg_data['message'].encode('utf-8'), 'FG_notice'))
            return None

        # User & room information received when joining a channel)
        if msg_data['type'] == "USERSTATE" or msg_data['type'] == "ROOMSTATE":
            return None

        # Usernotices are received when someone subscribes or raids the channel
        if msg_data['type'] == "USERNOTICE":
            self.parse_usernotice(msg_data, irc, queue)
            return None

        # CLEARCHAT is sent when a user has been timed out or banned
        if msg_data['type'] == "CLEARCHAT":
            reason = ""
            if len(msg_data['ban-reason']) > 0:
                reason = "Reason: " + " ".join(msg_data['ban-reason'].split('\\s'))

            if "ban-duration" in msg_data:
                queue.put(("@{0} has been timed out for {1} seconds. {2}".format(
                    msg_data['message'], msg_data['ban-duration'], reason), 'FG_notice'
                ))
            else: queue.put(("@{0} has been banned. {1}".format(msg_data['message'], reason), 'FG_notice'))
            return None

        # The last message type should be PRIVMSG, a regular chat message from a viewer
        if msg_data['type'] != "PRIVMSG":
            queue.put(("parse_socket_data() - Unrecognized message type '{0}'!".format(msg_data['type']), 'BG_error'))
            return None

        # Make sure the bot does not ever reply to itself
        if self.botname == None:
            self.botname = get_botname().encode('utf-8').lower()
        username = msg_data['display-name'].encode('utf-8').lower()
        if username == self.botname:
            return None

        message = msg_data['message'].encode('utf-8')
        queue.put((message, 'BG_chat', username, msg_data['color'], msg_data['mod'], msg_data['subscriber']))
        self.cron_value = 1 # Tell our cron manager that the chat has user activity

        # If the data contains a "bits" key, the chat message is a cheer
        if "bits" in msg_data:
            try:
                config = get_config()
                if int(msg_data['bits']) >= config['messages']['cheer']['limit']:
                    irc.send_custom_message("cheer", ['@' + username, msg_data['bits']])
            except KeyError:
                queue.put(("parse_socket_data() - Message config is corrupted!", 'BG_error'))
            return None

        # And finally, if the message starts with our command prefix,
        if not message.startswith("s!"):
            if message.startswith("@{0}".format(self.botname)): # Replace @bot with s!question
                message = "s!question {0}".format(message)
            else: return None

        command = message[2:].split(' ')[0]

        # Here are some (undesired) aliases for the !temperature command
        # This should not be the place for something like this
        if command in ["celsius", "fahrenheit", "kelvin"]:
            message = "s!temperature {0}".format(message[2:].lower())
            command = "temperature"

        # Since we now receive a user's mod status for every message, we can update the mod list here
        if msg_data['mod'] == '1' or "broadcaster" in msg_data['badges']:
            add_mod(username)
        elif self.check_mod_only(command):
            return None

        return (username, message, command)

    def parse_usernotice(self, msg_data, irc, queue):
        """Send back custom messages with relevant data when someone subscribes or raids the channel."""
        if msg_data['msg-id'] == "sub" or msg_data['msg-id'] == "resub":
            irc.send_custom_message("sub", [
                '@' + msg_data['display-name'].encode('utf-8').lower(), # Subscriber's display name
                msg_data['msg-param-months'], # Number of consecutive months the user has subscribed for
                msg_data['msg-param-sub-plan'], # Type of subscription plan (Prime, 1000, 2000, 3000)
                msg_data['msg-param-sub-plan-name'] # Display name of the subscription plan
            ])
        elif msg_data['msg-id'] == "raid":
            try:
                config = get_config()
                if int(msg_data['msg-param-viewerCount']) >= config['messages']['raid']['limit']:
                    irc.send_custom_message("raid", [
                        msg_data['msg-param-displayName'], # Display name of the user raiding this channel
                        msg_data['msg-param-viewerCount'] # Number of viewers raiding this channel
                    ])
            except KeyError:
                queue.put(("parse_socket_data() - Message config is corrupted!", 'BG_error'))

    def check_command_enabled(self, command, queue):
        """Check if the given command is enabled."""
        try:
            if get_config()['commands'][command]['enabled']:
                return True
            else:
                queue.put(("Command '{0}' is disabled, ignoring request ...".format(command), 'BG_progress'))
                return False
        except KeyError:
            return False

    def check_mod_only(self, command):
        """Return true if the command is for mods only."""
        try:
            return get_config()['commands'][command]['mod_only']
        except KeyError:
            return False

    def get_command_module(self, command, queue):
        """Return the appropriate module for given command. None if we can't import it."""
        try:
            module = importlib.import_module('src.commands.{0}'.format(command))
            return module
        except ImportError:
            queue.put(("get_command_module() - Could not import module '{0}'!".format(command), 'BG_error'))
        return None

    def get_command_result(self, module, command, args):
        """Return the result (string) from given command in given module."""
        config = get_config()
        queue = args[0]
        try:
            result = getattr(module, command)(args)
            if result == None: # Commands return None if there was an error in the code
                return None
            queue.put(("[{0}]: {1}".format(config['irc']['username'], result.encode('utf-8')), 'BG_chat'))
            return result
        except AttributeError:
            queue.put(("get_command_result() - No function found in module '{0}'!".format(command), 'BG_error'))
        return None
