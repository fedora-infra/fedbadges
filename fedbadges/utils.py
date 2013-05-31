""" Utilities for fedbadges that don't quite fit anywhere else. """


def construct_substitutions(msg):
    """ Convert a fedmsg message into a dict of substitutions. """
    subs = {}
    for key1 in msg:
        if isinstance(msg[key1], dict):
            subs.update(dict([
                ('_'.join([key1, key2]), val2)
                for key2, val2 in construct_substitutions(msg[key1]).items()
            ]))
        else:
            subs[key1] = msg[key1]
    return subs


def format_args(obj, subs):
    """ Recursively apply a substitutions dict to a given criteria subtree """

    if isinstance(obj, dict):
        for key in obj:
            obj[key] = format_args(obj[key], subs)
    elif isinstance(obj, list):
        return [format_args(item, subs) for item in obj]
    else:
        obj = obj.format(**subs)

    return obj
