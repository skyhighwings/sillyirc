#!/usr/bin/env python3

import socket

# TODO: config file!
servers = [
        {
            "name": "ponychat",
            "address": "irc.ponychat.net",
            "port": 6697,
            "ssl": True,
            "autojoin_channels": [
                "#geek"
                ]
        }
        ]


class Server:

    """The representation of a server -- an abstraction from having to deal
    with raw sockets from the main loop."""

    def __init__(self, name, address, port, ssl, autojoin_channels):
        self.name = name
        self.address = address
        self.port = port
        self.ssl = ssl
        self.autojoin_channels = autojoin_channels

    def send_line(line):
        # TODO: check the number of bytes returned from this
        self.sock.send(line)

    def receive_line(line):
        parsed = irc.parse_line(line)
        handlers[parsed["verb"]](parsed_line)


def send_line(server, line, priority=99):
    """Sends a line to the given IRC server.

    TODO move this to a Server instance method

    :server: TODO what is a server?
    :line: TODO
    :priority: TODO
    :returns: TODO

    """
    print("{server} <<< {line}".format(server=server, line=line))
    pass


def main():
    for server_name, server_info in servers.iteritems():
        for channel in server_info["autojoin_channels"]:
            send_line(server_name, "JOIN {channel}".format(channel=channel))

if __name__ == '__main__':
    main()
