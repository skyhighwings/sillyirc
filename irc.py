# IRC utility functions module

from collections import namedtuple
import socket
import select
import irc

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

    def __init__(self, name, address, port, ssl, nick, user, realname, autojoin_channels):
        self.name = name
        self.address = address
        self.port = port
        self.ssl = ssl
        self.nick = nick
        self.user = user
        self.realname = realname
        self.autojoin_channels = autojoin_channels
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.handlers = {
            "PRIVMSG": self.handle_privmsg,
            "PING": self.handle_ping,
            "001": self.handle_register
        }

        self.sock.connect((self.address, self.port))

        self.send_line("NICK {nick}".format(nick=self.nick))
        self.send_line("USER {user} * * :{realname}".format(user=self.user, realname=self.realname))

        # This is obviously not working. Why?
        while True:
            (r, w, x) = select.select([self.sock], [self.sock], [self.sock])
            if(r):
                line = self.sock.recv(512)
                self.receive_line(line)

    def send_line(self, line):
        print("{server} <-- {line}".format(server=self.name, line=line))
        # TODO: check the number of bytes returned from this
        self.sock.send(line)

    def receive_line(self, line):
        print("{server} --> {line}".format(server=self.name, line=line))
        parsed = irc.Message.from_line(line)

        self.handlers.get(parsed.verb, self.default_handler)(parsed)

    def handle_ping(self, msg):
        self.send_line(' '.join(["PONG", ' '.join(msg.args)]))

    def handle_privmsg(self, msg):
        self.send_line("PRIVMSG #a-f :I got a message! :D")
        pass

    def handle_register(self, msg):
        for channel in self.autojoin_channels:
            self.send_line("JOIN {channel}".format(channel=channel))

    def default_handler(self, msg):
        pass

