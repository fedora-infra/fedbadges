""" Utilities for fedbadges that don't quite fit anywhere else. """

import types

import logging
log = logging.getLogger("moksha.hub")

import fedmsg
import requests

# This is used for our queries against pkgdb
from dogpile.cache import make_region
_cache = make_region()


# These are here just so they're available in globals()
# for compiling lambda expressions
import re
import fedmsg.config
import fedmsg.encoding
import fedmsg.meta

try:
    from fedmsg_meta_fedora_infrastructure.fasshim import nick2fas
except ImportError as e:
    log.warn("Could not import nick2fas: %r" % e)


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


def get_pkgdb_packages_for(config, user):
    """ Retrieve the list of packages where the specified user some acl.

    :arg config: a dict containing the fedmsg config
    :arg user: the fas user of the packager whose packages are of
        interest.
    :return: a set listing all the packages where the specified user has
        some ACL.

    """

    if not hasattr(_cache, 'backend'):
        _cache.configure(**config['fedbadges.rules.cache'])

    @_cache.cache_on_arguments()
    def _getter(user):
        if config.get('fedbadges.rules.utils.use_pkgdb2', True):
            return _get_pkgdb2_packages_for(config, user)
        else:
            return _get_pkgdb1_packages_for(config, user)

    return _getter(user)


def _get_pkgdb2_packages_for(config, username):
    log.debug("Requesting pkgdb2 packages for user %r" % username)

    def _get_page(page):
        req = requests.get('{0}/packager/acl/{1}'.format(
            config['fedbadges.rules.utils.pkgdb_url'], username),
            params=dict(page=page),
        )

        if not req.status_code == 200:
            return set()

        return req.json()

    # We have to request the first page of data to figure out the total number
    data = _get_page(1)
    pages = data['page_total']

    packages = set()
    for i in range(1, pages + 1):

        # Avoid requesting the data twice the first time around
        if i != 1:
            data = _get_pages(i)

        for pkgacl in data['acls']:
            if pkgacl['status'] != 'Approved':
                continue

            packages.add(pkgacl['packagelist']['package']['name'])

    log.debug("done talking with pkgdb2 for now.")
    return packages


# TODO -- delete this once pkgdb2 goes live.
def _get_pkgdb1_packages_for(config, username):
    log.debug("Requesting pkgdb1 packages for user %r" % username)

    pkgdb1_base_url = config['fedbadges.rules.utils.pkgdb_url']
    query_string = "tg_format=json&pkgs_tgp_limit=10000"

    req = requests.get('{0}/users/packages/{1}?{2}'.format(
        pkgdb1_base_url, username, query_string))

    if not req.status_code == 200:
        return set()

    data = req.json()
    packages = set([pkg['name'] for pkg in data['pkgs']])
    log.debug("done talking with pkgdb1 for now.")
    return packages
