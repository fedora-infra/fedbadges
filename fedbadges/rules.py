# -*- coding; utf-8 -*-
""" Models for fedbadges.

The primary thing here is a "BadgeRule" which is an in-memory working
abstraction of the trigger and criteria required to award a badge.

Authors:    Ralph Bean
"""

import abc
import copy
import json
import types
import functools
import inspect
import transaction
import re

import fedmsg.config
import fedmsg.meta
import fedmsg.encoding
import datanommer.models

from fedbadges.utils import (
    # These are all in-process utilities
    construct_substitutions,
    format_args,
    single_argument_lambda_factory,
    recursive_lambda_factory,
    graceful,
    get_pagure_authors,

    # These make networked API calls
    user_exists_in_fas,
)

import logging
log = logging.getLogger('moksha.hub')


nick2fas = None
try:
    from fedmsg_meta_fedora_infrastructure.fasshim import nick2fas
except ImportError as e:
    log.warn("Could not import nick2fas: %r" % e)


email2fas = None
try:
    from fedmsg_meta_fedora_infrastructure.fasshim import email2fas
except ImportError as e:
    log.warn("Could not import email2fas: %r" % e)

# Match OpenID agent strings, i.e. http://FAS.id.fedoraproject.org
def openid2fas(openid, **config):
    m = re.search('^https?://([a-z][a-z0-9]+)\.id\.fedoraproject\.org$', openid)
    if m:
        return m.group(1)
    return openid

operators = frozenset([
    "all",
    "any",
    "not",
])
lambdas = frozenset([
    "lambda",
])

operator_lookup = {
    "any": any,
    "all": all,
    "not": lambda x: all([not item for item in x])
}

fedmsg_config = fedmsg.config.load_config()
fedmsg.meta.make_processors(**fedmsg_config)


class BadgeRule(object):
    required = frozenset([
        'name',
        'image_url',
        'description',
        'creator',
        'discussion',
        'issuer_id',

        'trigger',
        'criteria',
    ])

    possible = required.union([
        'recipient',
        'recipient_nick2fas',
        'recipient_email2fas',
        'recipient_openid2fas',
    ])

    banned_usernames = frozenset([
        'bodhi',
        'oscar',
        'apache',
        'koji',
        'bodhi',
        'taskotron',
    ])

    def __init__(self, badge_dict, tahrir_database, issuer_id):
        argued_fields = frozenset(badge_dict.keys())

        if not argued_fields.issubset(self.possible):
            raise KeyError(
                "%r are not possible fields.  Choose from %r" % (
                    argued_fields.difference(self.possible),
                    self.possible
                ))

        if not self.required.issubset(argued_fields):
            raise ValueError(
                "BadgeRule requires %r.  Missing %r" % (
                    self.required,
                    self.required.difference(argued_fields),
                ))

        self._d = badge_dict

        self.tahrir = tahrir_database
        if self.tahrir:
            transaction.begin()
            self.badge_id = self._d['badge_id'] = self.tahrir.add_badge(
                name=self._d['name'],
                image=self._d['image_url'],
                desc=self._d['description'],
                criteria=self._d['discussion'],
                tags=','.join(self._d.get('tags', [])),
                issuer_id=issuer_id,
            )
            transaction.commit()

        self.trigger = Trigger(self._d['trigger'], self)
        self.criteria = Criteria(self._d['criteria'], self)
        self.recipient_key = self._d.get('recipient')
        self.recipient_nick2fas = self._d.get('recipient_nick2fas')
        self.recipient_email2fas = self._d.get('recipient_email2fas')
        self.recipient_openid2fas = self._d.get('recipient_openid2fas')

        # A sanity check before we kick things off.
        if self.recipient_nick2fas and not nick2fas:
            raise ImportError("recipient_nick2fas specified, but "
                              "nick2fas is not available.")

        if self.recipient_email2fas and not email2fas:
            raise ImportError("recipient_email2fas specified, but "
                              "email2fas is not available.")

    def __getitem__(self, key):
        return self._d[key]

    def __repr__(self):
        return "<fedbadges.models.BadgeRule: %r>" % self._d

    def matches(self, msg):

        # First, do a lightweight check to see if the msg matches a pattern.
        if not self.trigger.matches(msg):
            return set()

        # Before proceeding further, let's see who would get this badge if
        # our more heavyweight checks matched up.  If the user specifies a
        # recipient_key, we can use that to extract the potential awardee.  If
        # that is not specified, we just use `msg2usernames`.
        if self.recipient_key:
            subs = construct_substitutions(msg)
            obj = format_args(self.recipient_key, subs)

            if isinstance(obj, (basestring, int, float)):
                obj = [obj]

            # On the way, it is possible for the fedmsg message to contain None
            # for "agent".  A problem here though is that None is not iterable,
            # so let's replace it with an equivalently empty iterable so code
            # further down doesn't freak out.  An instance of this is when a
            # user without a fas account comments on a bodhi update.
            if obj is None:
                obj = []


            # It is possible to recieve a list of dictionary containing the name
            # of the recipient, this is the case in the pagure's fedmsg.
            # In that case we create a new list containing the names taken from the
            # dictionnary.

            new_obj = get_pagure_authors(obj)
            if new_obj:
                obj = new_obj

            awardees = frozenset(obj)

            if self.recipient_nick2fas:
                awardees = frozenset([
                    nick2fas(nick, **fedmsg_config) for nick in awardees
                ])

            if self.recipient_email2fas:
                awardees = frozenset([
                    email2fas(email, **fedmsg_config) for email in awardees
                ])

            if self.recipient_openid2fas:
                awardees = frozenset([
                    openid2fas(openid, **fedmsg_config) for openid in awardees
                ])
        else:
            usernames = fedmsg.meta.msg2usernames(msg)
            awardees = usernames.difference(self.banned_usernames)

        # Strip anyone who is an IP address
        awardees = frozenset([
            user for user in awardees if not (
                user.startswith('192.168.') or
                user.startswith('10.')
            )
        ])

        # If no-one would get the badge by default, then no reason to waste
        # time doing any further checks.  No need to query the Tahrir DB.
        if not awardees:
            return awardees

        # Limit awardees to only those who do not already have this badge.
        # Do this only if we have an active connection to the Tahrir DB.
        if self.tahrir:
            awardees = frozenset([
                user for user in awardees
                if not self.tahrir.assertion_exists(
                    self.badge_id, "%s@fedoraproject.org" % user
                )])

            # Also, exclude any potential awardees who have opted out.
            awardees = frozenset([
                user for user in awardees
                if not self.tahrir.person_opted_out(
                    "%s@fedoraproject.org" % user
                )])

        # If no-one would get the badge at this point, then no reason to waste
        # time doing any further checks.  No need to query datanommer.
        if not awardees:
            return awardees

        # Check our backend criteria -- likely, perform datanommer queries.
        try:
            if not self.criteria.matches(msg):
                return set()
        except IOError as e:
            log.exception(e)
            return set()

        # Lastly, and this is probably most expensive.  Make sure the person
        # actually has a FAS account before we award anything.
        # https://github.com/fedora-infra/tahrir/issues/225
        awardees = set([
            u for u in awardees if user_exists_in_fas(fedmsg_config, u)
        ])

        return awardees


class AbstractComparator(object):
    """ Base class for shared behavior between trigger and criteria. """
    __metaclass__ = abc.ABCMeta
    possible = required = frozenset()
    children = None

    def __init__(self, d, parent=None):
        argued_fields = frozenset(d.keys())
        if not argued_fields.issubset(self.possible):
            raise KeyError(
                "%r are not possible fields.  Choose from %r" % (
                    argued_fields.difference(self.possible),
                    self.possible
                ))

        if self.required and not self.required.issubset(argued_fields):
            raise ValueError(
                "%r are required fields.  Missing %r" % (
                    self.required,
                    self.required.difference(argued_fields),
                ))

        self._d = d
        self.parent = parent

    def __repr__(self):
        return "<%s: %r> which is a child of %s" % (
            type(self).__name__, self._d, repr(self.parent)
        )

    @abc.abstractmethod
    def matches(self, msg):
        pass


class AbstractTopLevelComparator(AbstractComparator):
    def __init__(self, *args, **kwargs):
        super(AbstractTopLevelComparator, self).__init__(*args, **kwargs)
        cls = type(self)

        if len(self._d) > 1:
            raise ValueError("No more than one trigger allowed.  "
                             "Use an operator, one of %r" % operators)

        self.attribute = self._d.keys()[0]
        self.expected_value = self._d[self.attribute]

        # XXX - Check if we should we recursively nest Trigger/Criteria?

        # First, trick negation into thinking it is not a unary operator.
        if self.attribute == 'not':
            self.expected_value = [self.expected_value]

        # Then, treat everything as if it accepts an arbitrary # of args.
        if self.attribute in operators:
            if not isinstance(self.expected_value, list):
                raise TypeError("Operators only accept lists, not %r" %
                                type(self.expected_value))
            self.children = [cls(child, self) for child in self.expected_value]


class Trigger(AbstractTopLevelComparator):
    possible = frozenset([
        'topic',
        'category',
    ]).union(operators).union(lambdas)

    @graceful(set())
    def matches(self, msg):
        # Check if we should just aggregate the results of our children.
        # Otherwise, we are a leaf-node doing a straightforward comparison.
        if self.children:
            return operator_lookup[self.attribute]((
                child.matches(msg) for child in self.children
            ))
        elif self.attribute == 'lambda':
            return single_argument_lambda_factory(
                expression=self.expected_value, argument=msg, name='msg')
        elif self.attribute == 'category':
            # TODO -- use fedmsg.meta.msg2processor(msg).__name__.lower()
            return msg['topic'].split('.')[3] == self.expected_value
        else:
            if hasattr(msg[self.attribute], 'endswith'):
                return msg[self.attribute].endswith(self.expected_value)
            else:
                return msg[self.attribute] == self.expected_value


class Criteria(AbstractTopLevelComparator):
    possible = frozenset([
        'datanommer',
    ]).union(operators)

    def __init__(self, *args, **kwargs):
        super(Criteria, self).__init__(*args, **kwargs)

        if not self.children:
            # Then, by AbstractComparator rules, I am a leaf node.  Specialize!
            self._specialize()

    def _specialize(self):
        if self.attribute == 'datanommer':
            self.specialization = DatanommerCriteria(self.expected_value)
        # TODO -- expand this with other "backends" as necessary
        # elif self.attribute == 'fas'
        else:
            raise RuntimeError("This should be impossible to reach.")

    @graceful(set())
    def matches(self, msg):
        if self.children:
            return operator_lookup[self.attribute]((
                child.matches(msg) for child in self.children
            ))
        else:
            return self.specialization.matches(msg)


class AbstractSpecializedComparator(AbstractComparator):
    pass

class DatanommerCriteria(AbstractSpecializedComparator):
    required = possible = frozenset([
        'filter',
        'operation',
        'condition',
    ])

    condition_callbacks = {
        'is greater than or equal to': lambda t, v: v >= t,
        'greater than or equal to': lambda t, v: v >= t,
        'greater than': lambda t, v: v > t,

        'is less than or equal to': lambda t, v: v <= t,
        'less than or equal to': lambda t, v: v <= t,
        'less than': lambda t, v: v < t,

        'equal to': lambda t, v: v == t,
        'is equal to': lambda t, v: v == t,

        'is not': lambda t, v: v != t,
        'is not equal to': lambda t, v: v != t,

        'lambda': single_argument_lambda_factory,
    }

    def __init__(self, *args, **kwargs):
        super(DatanommerCriteria, self).__init__(*args, **kwargs)
        if len(self._d['condition']) > 1:
            conditions = self.condition_callbacks.keys()
            raise ValueError("No more than one condition allowed.  "
                             "Use one of %r" % conditions)

        # Determine what arguments datanommer..grep accepts
        argspec = inspect.getargspec(datanommer.models.Message.grep)
        irrelevant = frozenset(['defer'])
        grep_arguments = frozenset(argspec.args[1:]).difference(irrelevant)

        # Validate the filter
        argued_filter_fields = frozenset(self._d['filter'].keys())
        if not argued_filter_fields.issubset(grep_arguments):
            raise KeyError(
                "%r are not possible fields.  Choose from %r" % (
                    argued_filter_fields.difference(grep_arguments),
                    grep_arguments,
                ))

        # Validate the condition
        condition_key, condition_val = self._d['condition'].items()[0]
        if condition_key not in self.condition_callbacks:
            raise KeyError("%r is not a valid condition key.  Use one of %r" %
                           (condition_key, self.condition_callbacks.keys()))

        # Construct a condition callable for later
        self.condition = functools.partial(
            self.condition_callbacks[condition_key], condition_val)

    def _construct_query(self, msg):
        """ Construct a datanommer query for this message.

        The "filter" section of this criteria object will be used.  It will
        first be formatted with any substitutions present in the incoming
        message.  This is used, for instance, to construct a query like "give
        me all the messages bearing the same topic as the message that just
        arrived".
        """
        subs = construct_substitutions(msg)
        kwargs = format_args(copy.copy(self._d['filter']), subs)
        kwargs = recursive_lambda_factory(kwargs, msg, name='msg')

        # It is possible to recieve a list of dictionary containing the name
        # of the recipient, this is the case in the pagure's fedmsg.
        # In that case we create a new list containing the names taken from the
        # dictionnary.
        if kwargs.get('users') is not None:
            for item in kwargs['users']:
                if isinstance(item, list):
                    kwargs['users'] = item
            users = get_pagure_authors(kwargs['users'])
            if users:
                kwargs['users'] = users
        kwargs['defer'] = True
        total, pages, query = datanommer.models.Message.grep(**kwargs)
        return total, pages, query

    def _format_lambda_operation(self, msg):
        """ Format the string representation of a lambda operation.

        The lambda operation can be formatted here to include strings that
        appear in the message being evaluated like
        %(msg.comment.update_submitter)s.  Placeholders like that will have
        their value substituted with whatever appears in the incoming message.
        """
        subs = construct_substitutions(msg)
        operation = format_args(copy.copy(self._d['operation']), subs)
        return operation['lambda']

    def matches(self, msg):
        """ A datanommer criteria check is composed of three steps.

        - A datanommer query is constructed by combining our yaml definition
          with the incoming fedmsg message that triggered us.
        - An operation in python is constructed by comining our yaml definition
          with the incoming fedmsg message that triggered us.  That operation
          is then executed against the datanommer query object.
        - A condition, derived from our yaml definition, is evaluated with the
          result of the operation from the previous step and is returned.
        """
        total, pages, query = self._construct_query(msg)
        if self._d['operation'] == 'count':
            result = total
        elif isinstance(self._d['operation'], dict):
            expression = self._format_lambda_operation(msg)
            result = single_argument_lambda_factory(
                expression=expression, argument=query, name='query')
        else:
            operation = getattr(query, self._d['operation'])
            result = operation()
        return self.condition(result)
