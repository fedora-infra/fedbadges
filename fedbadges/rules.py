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

import fedmsg.config
import fedmsg.meta
import fedmsg.encoding
import datanommer.models

from fedbadges.utils import (
    construct_substitutions,
    format_args,
    single_argument_lambda_factory,
    recursive_lambda_factory,
    graceful,
)

import logging
log = logging.getLogger('moksha.hub')


nick2fas = None
try:
    from fedmsg_meta_fedora_infrastructure.fasshim import nick2fas
except ImportError as e:
    log.warn("Could not import nick2fas: %r" % e)


operators = set([
    "all",
    "any",
    #"not",
])
lambdas = set([
    "lambda",
])

operator_lookup = {
    "any": any,
    "all": all,
}

fedmsg_config = fedmsg.config.load_config()
fedmsg.meta.make_processors(**fedmsg_config)


class BadgeRule(object):
    required = set([
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
    ])

    banned_usernames = set([
        'bodhi',
        'oscar',
        'apache',
        'koji',
    ])

    def __init__(self, badge_dict, tahrir_database, issuer_id):
        argued_fields = set(badge_dict.keys())

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

        # A sanity check before we kick things off.
        if self.recipient_nick2fas and not nick2fas:
            raise ImportError("recipient_nick2fas specified, but "
                              "nick2fas is not available.")

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

            awardees = set(obj)

            if self.recipient_nick2fas:
                awardees = set([
                    nick2fas(nick, **fedmsg_config) for nick in awardees
                ])
        else:
            usernames = fedmsg.meta.msg2usernames(msg)
            awardees = usernames.difference(self.banned_usernames)

        # Strip anyone who is an IP address
        awardees = set([
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
            awardees = set([user for user in awardees
                            if not self.tahrir.assertion_exists(
                                self.badge_id, "%s@fedoraproject.org" % user
                            )])

            # Also, exclude any potential awardees who have opted out.
            awardees = set([user for user in awardees
                            if not self.tahrir.person_opted_out(
                                "%s@fedoraproject.org" % user
                            )])

        # If no-one would get the badge at this point, then no reason to waste
        # time doing any further checks.  No need to query datanommer.
        if not awardees:
            return awardees

        # Check our backend criteria -- likely, perform datanommer queries.
        if not self.criteria.matches(msg):
            return set()

        return awardees


class AbstractComparator(object):
    """ Base class for shared behavior between trigger and criteria. """
    __metaclass__ = abc.ABCMeta
    possible = required = set()
    children = None

    def __init__(self, d, parent=None):
        argued_fields = set(d.keys())
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

        # Check if we should we recursively nest Trigger/Criteria?
        if self.attribute in operators:
            if not isinstance(self.expected_value, list):
                raise TypeError("Operators only accept lists, not %r" %
                                type(self.expected_value))
            self.children = [cls(child, self) for child in self.expected_value]


class Trigger(AbstractTopLevelComparator):
    possible = set([
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
    possible = set([
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
        #elif self.attribute == 'fas'
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
    required = possible = set([
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
        irrelevant = set(['defer'])
        grep_arguments = set(argspec.args[1:]).difference(irrelevant)

        # Validate the filter
        argued_filter_fields = set(self._d['filter'].keys())
        if not argued_filter_fields.issubset(grep_arguments):
            raise KeyError(
                "%r are not possible fields.  Choose from %r" % (
                    argued_filter_fields.difference(grep_arguments),
                    grep_arguments,
                ))

        # Validate the condition
        condition_key, condition_val = self._d['condition'].items()[0]
        if not condition_key in self.condition_callbacks:
            raise KeyError("%r is not a valid condition key.  Use one of %r" %
                           (condition_key, self.condition_callbacks.keys()))

        # Construct a condition callable for later
        self.condition = functools.partial(
            self.condition_callbacks[condition_key], condition_val)

    def construct_query(self, msg):
        subs = construct_substitutions(msg)
        kwargs = format_args(copy.copy(self._d['filter']), subs)
        kwargs = recursive_lambda_factory(kwargs, msg, name='msg')
        kwargs['defer'] = True
        total, pages, query = datanommer.models.Message.grep(**kwargs)
        return total, pages, query

    def matches(self, msg):
        total, pages, query = self.construct_query(msg)
        if self._d['operation'] == 'count':
            result = total
        elif isinstance(self._d['operation'], dict):
            expression = self._d['operation']['lambda']
            result = single_argument_lambda_factory(
                expression=expression, argument=query, name='query')
        else:
            operation = getattr(query, self._d['operation'])
            result = operation()
        return self.condition(result)
