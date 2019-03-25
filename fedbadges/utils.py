""" Utilities for fedbadges that don't quite fit anywhere else. """

import types

import logging
log = logging.getLogger("moksha.hub")

import fedmsg
import fedora.client
import requests

# These are here just so they're available in globals()
# for compiling lambda expressions
import json
import re
import fedmsg.config
import fedmsg.encoding
import fedmsg.meta


def construct_substitutions(msg):
    """ Convert a fedmsg message into a dict of substitutions. """
    subs = {}
    for key1 in msg:
        if isinstance(msg[key1], dict):
            subs.update(dict([
                ('.'.join([key1, key2]), val2)
                for key2, val2 in construct_substitutions(msg[key1]).items()
            ]))
            subs[key1] = msg[key1]
        elif isinstance(msg[key1], basestring):
            subs[key1] = msg[key1].lower()
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
    elif isinstance(obj, basestring) and obj[2:-2] in subs:
        obj = subs[obj[2:-2]]
    elif isinstance(obj, (int, float)):
        pass
    else:
        obj = obj % subs

    return obj


def single_argument_lambda_factory(expression, argument, name='value'):
    """ Compile and execute a lambda expression with a single argument """

    code = compile("lambda %s: %s" % (name, expression), __file__, "eval")
    func = types.LambdaType(code, globals())()
    return func(argument)


def recursive_lambda_factory(obj, arg, name='value'):
    """ Given a dict, find any lambdas, compile, and execute them. """

    if isinstance(obj, dict):
        for key in obj:
            if key == 'lambda':
                # If so, *replace* the parent dict with the result of the expr
                obj = single_argument_lambda_factory(obj[key], arg, name)
                break
            else:
                obj[key] = recursive_lambda_factory(obj[key], arg, name)
    elif isinstance(obj, list):
        return [recursive_lambda_factory(e, arg, name) for e in obj]
    else:
        pass

    return obj


def graceful(default_return_value):
    """ A decorator that gracefully handles exceptions. """

    def decorate(method):
        def inner(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                log.exception(e)
                log.error("From method: %r self: %r args: %r kwargs: %r" % (
                    method, self, args, kwargs))
                return default_return_value
        return inner
    return decorate


def notification_callback(topic, msg):
    """ This is a callback called by tahrir_api whenever something
    it deems important has happened.

    It is just used to publish fedmsg messages.
    """
    fedmsg.publish(
        topic=topic,
        msg=msg,
    )


def user_exists_in_fas(config, user):
    """ Return true if the user exists in FAS. """
    default_url = 'https://admin.fedoraproject.org/accounts/'
    fas2 = fedora.client.AccountSystem(
        base_url=config['fas_credentials'].get('base_url', default_url),
        username=config['fas_credentials']['username'],
        password=config['fas_credentials']['password'],
    )
    return bool(fas2.person_by_username(user))

def get_pagure_authors(authors):
    """ Extract the name of pagure authors from
    a dictionary

    Args:
    authors (list): A list of dict that contains fullname and name key.
    """
    authors_name = []
    for item in authors:
        if isinstance(item, dict):
            try:
                authors_name.append(item["name"])
            except KeyError:
                raise Exception("Multiple recipients : name not found in the message")
    return authors_name
