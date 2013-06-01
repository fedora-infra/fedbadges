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

import fedmsg.config
import fedmsg.meta
import fedmsg.encoding
import datanommer.models

from fedbadges.utils import (
    construct_substitutions,
    format_args,
    single_argument_lambda_factory,
    recursive_lambda_factory,
)

operators = set([
    "all",
    "any",
    #"not",
])
lambdas = set([
    "lambda",
])

fedmsg_config = fedmsg.config.load_config()
fedmsg.meta.make_processors(**fedmsg_config)


class BadgeRule(object):
    required = set([
        'name',
        'description',
        'creator',
        'discussion',
        'trigger',
        'criteria',
    ])

    def __init__(self, badge_dict):
        argued_fields = set(badge_dict.keys())
        if not self.required.issubset(argued_fields):
            raise ValueError(
                "BadgeRule requires %r.  Missing %r" % (
                    self.required,
                    self.required.difference(argued_fields),
                ))

        self._d = badge_dict

        self.trigger = Trigger(self._d['trigger'])
        self.criteria = Criteria(self._d['criteria'])

    def __getitem__(self, key):
        return self._d[key]

    def matches(self, msg):
        if not self.trigger.matches(msg):
            return False
        if not self.criteria.matches(msg):
            return False
        return True


class AbstractComparator(object):
    """ Base class for shared behavior between trigger and criteria. """
    __metaclass__ = abc.ABCMeta
    possible = required = set()
    children = None

    def __init__(self, d):
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

    @abc.abstractmethod
    def matches(self, msg):
        pass


class AbstractTopLevelComparator(AbstractComparator):
    def __init__(self, d):
        super(AbstractTopLevelComparator, self).__init__(d)
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
            self.children = [cls(child) for child in self.expected_value]


class Trigger(AbstractTopLevelComparator):
    possible = set([
        'topic',
        'category',
    ]).union(operators).union(lambdas)

    def matches(self, msg):
        # Check if we should just aggregate the results of our children.
        # Otherwise, we are a leaf-node doing a straightforward comparison.
        if self.children:
            return __builtins__[self.attribute]([
                child.matches(msg) for child in self.children
            ])
        elif self.attribute == 'lambda':
            source = "lambda msg: " + self.expected_value
            code = compile(source, __file__, "eval")
            func = types.LambdaType(code, globals())()
            return func(msg)
        elif self.attribute == 'category':
            # TODO -- use fedmsg.meta.msg2processor(msg).__name__.lower()
            return msg['topic'].split('.')[3] == self.expected_value
        else:
            return msg[self.attribute] == self.expected_value


class Criteria(AbstractTopLevelComparator):
    possible = set([
        'datanommer',
    ]).union(operators)

    def __init__(self, d):
        super(Criteria, self).__init__(d)

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

    def matches(self, msg):
        if self.children:
            return __builtins__[self.attribute]([
                child.matches(msg) for child in self.children
            ])
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
        'greater than or equal to': lambda t, v: v >= t,
        'greater than': lambda t, v: v > t,
        'less than or equal to': lambda t, v: v <= t,
        'less than': lambda t, v: v < t,
        'equal to': lambda t, v: v == t,
        'is not': lambda t, v: v != t,
        'lambda': single_argument_lambda_factory,
    }

    def __init__(self, d):
        super(DatanommerCriteria, self).__init__(d)
        if len(self._d['condition']) > 1:
            conditions = self.condition_callbacks.keys()
            raise ValueError("No more than one condition allowed.  "
                             "Use one of %r" % conditions)

        # Determine what arguments datanommer..grep accepts
        argspec = inspect.getargspec(datanommer.models.Message.grep)
        irrelevant = set(['rows_per_page', 'page', 'defer'])
        grep_arguments = set(argspec.args[1:]).difference(irrelevant)

        # Validate the filter
        argued_filter_fields = set(d['filter'].keys())
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
        return query

    def matches(self, msg):
        query = self.construct_query(msg)
        operation = getattr(query, self._d['operation'])
        result = operation()
        return self.condition(result)
