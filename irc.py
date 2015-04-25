# IRC utility functions module

from collections import namedtuple
import queue
import socket
import select
import irc
import time


class NotConnectedException(Exception):
    pass


# Adapted from Tarn's message parser (https://github.com/aerdan/tarn)
class Message(namedtuple("Message", ["tags", "source", "verb", "args"])):
    """
    Representation of a message as a namedtuple.
    """

    @classmethod
    def from_line(clz, line):
        fields = line.split(" ")
        message = {
            "tags": {},
            "source": None,
            "verb": None,
            "args": []
        }

        # If this is present, then we have tags, else we don't.
        if fields[0].startswith("@"):
            field = fields.pop(0)[1:]
            tags = field.split(";")

            for tag in tags:
                if "=" in tag:
                    key, val = tag.split("=", 1)
                else:
                    key, val = tag, True

                message["tags"][key] = val

        if fields[0].startswith(":"):
            message["source"] = fields.pop(0)[1:]

        message["verb"] = fields.pop(0)

        for i in range(0, len(fields)):
            field = fields[i]

            if field.startswith(":"):
                message["args"].append(' '.join(fields[i:])[1:])
                break

            else:
                message["args"].append(field)

        return clz(**message)


class Server:

    """The representation of a server -- an abstraction from having to deal
    with raw sockets from the main loop."""

    def __init__(self,
                 name,
                 address,
                 port,
                 ssl,
                 nick,
                 user,
                 realname,
                 autojoin_channels):
        self.name = name
        self.address = address
        self.port = port
        self.ssl = ssl
        self.nick = nick
        self.user = user
        self.realname = realname
        self.autojoin_channels = autojoin_channels
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.tmp_buf = b''
        self.sendq = queue.Queue()

        self.handlers = {
            "PRIVMSG": self.handle_privmsg,
            "PING": self.handle_ping,
            "001": self.handle_register
        }

        self.sock.connect((self.address, self.port))

        self.send_line("NICK {nick}".format(nick=self.nick))
        self.send_line("USER {user} * * :{realname}"
                       .format(user=self.user, realname=self.realname))
        self.last_sent = time.time()


    def process(self):
        (r,_, x) = select.select([self.sock], [], [self.sock], 0)
        (_,w,_) = select.select([], [self.sock], [], 0)

        if len(r) > 0:
            data = self.tmp_buf + self.sock.recv(512).replace(b'\r', b'')
            lines = data.split(b'\n')
            self.tmp_buf = lines[-1]

            for line in lines[:-1]:
                self.receive_line(line.decode('utf-8'))

        if len(w) > 0:
            try:
                if time.time() - self.last_sent > 1:
                    line = self.sendq.get(False)

                    print("{server} <-- {line}".format(server=self.name,
                                                       line=line))
                    self.sock.send(line.encode('utf-8') + b'\r\n')

                    self.last_sent = time.time()
            except queue.Empty:
                pass

        if len(x) > 0:
            raise irc.NotConnectedException()

    def send_line(self, line):
        self.sendq.put(line)

    def receive_line(self, line):
        print("{server} --> {line}".format(server=self.name, line=line))
        parsed = irc.Message.from_line(line)

        self.handlers.get(parsed.verb, self.default_handler)(parsed)

    def handle_ping(self, msg):
        self.send_line(' '.join(["PONG", ' '.join(msg.args)]))

    def handle_privmsg(self, msg):
        self.send_line("PRIVMSG #sillybot :I got a message! :D")
        pass

    def handle_register(self, msg):
        for channel in self.autojoin_channels:
            self.send_line("JOIN {channel}".format(channel=channel))

    def default_handler(self, msg):
        pass
