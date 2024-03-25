""" Utilities for fedbadges that don't quite fit anywhere else. """

# These are here just so they're available in globals()
# for compiling lambda expressions
import json  # noqa: F401
import logging
import re  # noqa: F401
import sys
import traceback
import types

import backoff
from fedora_messaging import api as fm_api
from fedora_messaging import exceptions as fm_exceptions


log = logging.getLogger(__name__)


def construct_substitutions(msg: dict):
    """Convert a fedmsg message into a dict of substitutions."""
    subs = {}
    for key1 in msg:
        if isinstance(msg[key1], dict):
            subs.update(
                dict(
                    [
                        (".".join([key1, key2]), val2)
                        for key2, val2 in list(construct_substitutions(msg[key1]).items())
                    ]
                )
            )
            subs[key1] = msg[key1]
        elif isinstance(msg[key1], str):
            subs[key1] = msg[key1].lower()
        else:
            subs[key1] = msg[key1]
    return subs


def format_args(obj, subs):
    """Recursively apply a substitutions dict to a given criteria subtree"""

    if isinstance(obj, dict):
        for key in obj:
            obj[key] = format_args(obj[key], subs)
    elif isinstance(obj, list):
        return [format_args(item, subs) for item in obj]
    elif isinstance(obj, str) and obj[2:-2] in subs:
        obj = subs[obj[2:-2]]
    elif isinstance(obj, (int, float)):
        pass
    else:
        obj = obj % subs

    return obj


def single_argument_lambda_factory(expression, argument, name="value"):
    """Compile and execute a lambda expression with a single argument"""

    code = compile("lambda {name}: {expression}", __file__, "eval")
    func = types.LambdaType(code, globals())()
    return func(argument)


def recursive_lambda_factory(obj, arg, name="value"):
    """Given a dict, find any lambdas, compile, and execute them."""

    if isinstance(obj, dict):
        for key in obj:
            if key == "lambda":
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
    """A decorator that gracefully handles exceptions."""

    def decorate(method):
        def inner(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                log.exception(e)
                log.error(
                    "From method: %r self: %r args: %r kwargs: %r", method, self, args, kwargs
                )
                return default_return_value

        return inner

    return decorate


def _backoff_hdlr(details):
    log.warning(f"Publishing message failed. Retrying. {traceback.format_tb(sys.exc_info()[2])}")


@backoff.on_exception(
    backoff.expo,
    (fm_exceptions.ConnectionException, fm_exceptions.PublishException),
    max_tries=3,
    on_backoff=_backoff_hdlr,
)
def _publish(message):
    fm_api.publish(message)


def notification_callback(topic, msg):
    """This is a callback called by tahrir_api whenever something
    it deems important has happened.

    It is just used to publish fedmsg messages.
    """
    message = fm_api.Message(topic=topic, body=msg)
    try:
        _publish(message)
    except fm_exceptions.BaseException:
        log.error(f"Publishing message failed. Giving up. {traceback.format_tb(sys.exc_info()[2])}")


def user_exists_in_fas(fasjson, user):
    """Return true if the user exists in FAS."""
    return fasjson.get_user(user) is not None


def get_pagure_authors(authors):
    """Extract the name of pagure authors from
    a dictionary

    Args:
    authors (list): A list of dict that contains fullname and name key.
    """
    authors_name = []
    for item in authors:
        if isinstance(item, dict):
            try:
                if item["name"] is not None:
                    authors_name.append(item["name"])
            except KeyError as e:
                raise Exception("Multiple recipients : name not found in the message") from e
    return authors_name


def nick2fas(nick, fasjson):
    """Return the user in FAS."""
    return fasjson.get_user(nick)


def email2fas(email, fasjson):
    """Return the user with the specified email in FAS."""
    if email.endswith("@fedoraproject.org"):
        return nick2fas(email.rsplit("@", 1)[0], fasjson)

    result = fasjson.search_users(email__exact=email)
    if not result:
        return None
    return result[0]
