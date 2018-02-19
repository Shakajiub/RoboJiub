import re
import sys
import socket

from src.config.config import *

class IRC:
    def __init__(self, queue):
        self.queue = queue

    def end_connection(self):
        """Send a goodbye message through irc and close the socket."""
        try:
            self.send_custom_message('goodbye')
            channel = get_channel()
            if channel:
                self.sock.send('PART {0}\r\n'.format(channel))
            self.sock.close()
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.end_connection() - Could not close socket!", 'BG_error'))

    def check_for_message(self, data, queue):
        """Parse data from twitch into a nice dictionary."""
        try:
            data = data.decode('utf-8').split(" :")
        except UnicodeDecodeError:
            # TODO - This generally means the message is spam, so /timeout the user
            queue.put(("check_for_message() - Can't decode chat message!", 'BG_error'))
            return False

        # TODO - Parse USERSTATE and ROOMSTATE
        if len(data) > 1 and len(data) < 4 and len(data[1].split(' ')) > 1:
            msg_type = data[1].split(' ')[1]
            msg_data = { 'type': msg_type }

            params = data[0].split(';')
            for param in params:
                p = param.split('=')
                msg_data[p[0]] = p[1]

            if len(data) > 2:
                msg_data['message'] = data[2][:-2]
            return msg_data

        else: print(data)
        return False

    def check_for_ping(self, data):
        """If given data starts with PING, send PONG + rest of the data back."""
        if data.startswith('PING'):
            try:
                self.sock.send('PONG {0}\r\n'.format(data[5:]))
            except Exception:
                self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
                self.queue.put(("irc.check_for_ping() - Could not respond with PONG!", 'BG_error'))

    def check_login_status(self, data):
        """Return false if given data says login was unsuccessful. True otherwise."""
        if re.match(r'^:(tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        return True

    def send_message(self, message):
        """Try to send given message as PRIVMSG through the irc socket."""
        if message == None:
            return
        try:
            channel = get_channel()
            if channel:
                self.sock.send('PRIVMSG {0} : {1}\n'.format(channel, message.encode('utf-8')))
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.send_message() - Could not send message!", 'BG_error'))

    def send_custom_message(self, message, data=None):
        """Try to send given message (if defined in the config)."""
        config = get_config()
        try:
            if config['messages'][message]['enabled']:
                self.send_message(self.format_custom_message(message, config['messages'][message]['msg'], data))
        except KeyError:
            self.queue.put(("irc.send_custom_message() - Could not send message '{0}'!".format(message), 'BG_error'))

    def format_custom_message(self, message, text, data):
        """Add relevant data to custom bot messages."""
        if message == "bits" and len(data) == 2:
            text = text.format(user=data[0], bits=data[1])
        elif message == "sub" and len(data) == 4:
            text = text.format(user=data[0], streak=data[1], tier=data[2], plan=data[3])
        return text

    def get_socket_object(self):
        """Connect and join irc channels as setup in the config. Return None or the socket."""
        config = get_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        self.sock = sock

        if not self.connect_socket(config):
            return None

        sock.settimeout(None)
        channel = self.login_socket(config)
        if not channel:
            return None

        self.sock.send('CAP REQ :twitch.tv/tags\r\n'.encode('utf-8'))
        self.sock.send('CAP REQ :twitch.tv/commands\r\n'.encode('utf-8'))

        self.sock.send('JOIN {0}\r\n'.format(channel))
        self.send_custom_message('greeting')
        return sock

    def connect_socket(self, config):
        """Connect our socket as defined in the config. Return true on success."""
        try:
            self.sock.connect((config['irc']['server'], config['irc']['port']))
            return True
        except KeyError:
            self.queue.put(("irc.connect_socket() - IRC config is corrupted!", 'BG_error'))
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.connect_socket() - Cannot connect to server!", 'BG_error'))
        return False

    def login_socket(self, config):
        """Login to the IRC channel as defined in the config. Return the channel name joined."""
        try:
            self.sock.send('USER {0}\r\n'.format(config['irc']['username']))
            self.sock.send('PASS {0}\r\n'.format(config['irc']['oauth_password']))
            self.sock.send('NICK {0}\r\n'.format(config['irc']['username']))
            channel = config['irc']['channel']
        except KeyError:
            self.queue.put(("irc.login_socket() - IRC config is corrupted!", 'BG_error'))
            return False
        if self.check_login_status(self.sock.recv(1024)):
            self.queue.put(("Login successful, joining channel {0}".format(channel), 'BG_success'))
        else:
            self.queue.put(("Login failed (possibly invalid oauth token)", 'BG_error'))
            return False
        return channel
