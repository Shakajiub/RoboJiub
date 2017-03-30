# TODO credit https://github.com/aidanrwt/twitch-bot
# TODO fix line lengths above 100

import re
import socket

from src.config.config import *

class IRC:
    """
    TODO description
    """
    def __init__(self, queue):
        self.queue = queue

    def end_connection(self):
        try:
            config = get_config()
            self.send_message(config["messages"]["goodbye"])
            self.sock.close()
        except: pass

    def check_for_message(self, data):
        if re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING":
            try:
                self.sock.send('PONG %s\r\n' % data[5:])
            except: pass

    def check_login_status(self, data):
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else: return True

    def send_message(self, message):
        config = get_config()
        try:
            self.sock.send('PRIVMSG %s :%s\n' % (config['irc']['channel'], message.encode('utf-8')))
        except: pass

    def get_message(self, data):
        return {
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
        }

    def get_irc_socket_object(self):
        config = get_config()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        self.sock = sock

        try:
            sock.connect((config['irc']['server'], config['irc']['port']))
        except:
            self.queue.put(('Cannot connect to server (%s:%s)' % (config['irc']['server'], config['irc']['port']), 'BG_error'))
            return None

        sock.settimeout(None)
        sock.send('USER %s\r\n' % config['irc']['username'])
        sock.send('PASS %s\r\n' % config['irc']['oauth_password'])
        sock.send('NICK %s\r\n' % config['irc']['username'])

        if self.check_login_status(sock.recv(1024)):
            self.queue.put(('Login successful, joining channel: %s' % config['irc']['channel'], 'BG_success'))
        else:
            self.queue.put(('Login failed! (possibly invalid oauth token)', 'BG_error'))
            return None

        self.sock.send('JOIN %s\r\n' % config['irc']['channel'])
        self.send_message(config["messages"]["greeting"])
        return sock
