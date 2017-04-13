import re
import sys
import socket

from src.config.config import get_config

class IRC:
    def __init__(self, queue):
        self.queue = queue

    def end_connection(self):
        """Send a goodbye message through irc and close the socket."""
        try:
            config = get_config()
            if config['messages']['enabled']:
                self.send_message(config['messages']['goodbye'])
            self.sock.close()
        except KeyError:
            self.queue.put(("irc.end_connection() - Message config is corrupted", 'BG_error'))
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.end_connection() - Could not close socket", 'BG_error'))

    def check_for_message(self, data):
        """Return true if given data contains a message from a viewer."""
        s = '[a-zA-Z0-9_]'
        if re.match(r'^:{0}+\!{0}+@{0}+(\.tmi\.twitch\.tv) PRIVMSG #{0}+ :.+$'.format(s), data):
            return True
        else:
            return False

    def check_for_ping(self, data):
        """If given data contains PING, send PONG + rest of the data through the irc socket."""
        if data.startswith('PING'):
            try:
                self.sock.send('PONG {0}\r\n'.format(data[5:]))
            except Exception:
                self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
                self.queue.put(("irc.check_for_ping() - Could not respond with PONG", 'BG_error'))

    def check_login_status(self, data):
        """Return false if given data says login was unsuccessful. True otherwise."""
        if re.match(r'^:(tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else:
            return True

    def send_message(self, message):
        """Try to send given message as PRIVMSG through the irc socket."""
        try:
            channel = get_config()['irc']['channel']
            self.sock.send('PRIVMSG {0} :{1}\n'.format(channel, message.encode('utf-8')))
        except KeyError:
            self.queue.put(("irc.send_message() - IRC config is corrupted", 'BG_error'))
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.send_message() - Could not send message", 'BG_error'))

    def get_message(self, data):
        """Return a dictionary containing the 'username' and the 'message' from given data."""
        return {
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
        }

    def get_socket_object(self):
        """Connect and join irc channels as setup in the config. Return None or the socket."""
        config = get_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        self.sock = sock
        try:
            sock.connect((config['irc']['server'], config['irc']['port']))
        except KeyError:
            self.queue.put(("irc.get_socket_object() - IRC config is corrupted", 'BG_error'))
            return None
        except Exception:
            self.queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
            self.queue.put(("irc.get_socket_object() - Cannot connect to server", 'BG_error'))
            return None

        sock.settimeout(None)
        try:
            sock.send('USER {0}\r\n'.format(config['irc']['username']))
            sock.send('PASS {0}\r\n'.format(config['irc']['oauth_password']))
            sock.send('NICK {0}\r\n'.format(config['irc']['username']))
            channel = config['irc']['channel']
        except KeyError:
            self.queue.put(("irc.get_socket_object() - IRC config is corrupted", 'BG_error'))
            return None

        if self.check_login_status(sock.recv(1024)):
            self.queue.put(("Login successful, joining channel {0}".format(channel), 'BG_success'))
        else:
            self.queue.put(("Login failed (possibly invalid oauth token)", 'BG_error'))
            return None
        try:
            self.sock.send('JOIN {0}\r\n'.format(channel))
            if config['messages']['enabled']:
                self.send_message(config['messages']['greeting'])
        except KeyError:
            self.queue.put(("irc.get_socket_object() - Message config is corrupted", 'BG_error'))
        return sock
