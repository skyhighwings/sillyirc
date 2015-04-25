# IRC utility functions module

from collections import namedtuple


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
