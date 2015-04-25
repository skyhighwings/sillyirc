#!/usr/bin/env python3

import irc

# TODO: config file!
servers = [
    {
        "name": "ponychat",
        "address": "irc.ponychat.net",
        "port": 6667,
        "ssl": True,
        "nick": "sillybot",
        "user": "sillybot",
        "realname": "sillybot by rylee",
        "autojoin_channels": [
            "#geek"
        ]
    }
]



def main():
    srvs = []
    for server in servers:
        srvs.append(irc.Server(**server))


if __name__ == '__main__':
    main()
