# -*- coding; utf-8 -*-
""" Models for fedbadges.

The primary thing here is a "BadgeRule" which is an in-memory working
abstraction of the trigger and criteria required to award a badge.

Authors:    Ralph Bean
"""

import abc



class BadgeRule(object):
    required_fields = [
        'name',
        'description',
        'creator',
        'discussion',
        'trigger',
        'criteria',
    ]

    def __init__(self, badge_dict):
        for field in self.required_fields:
            if not field in badge_dict:
                raise ValueError("BadgeRule requires %r" % field)

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


class BaseComparator(object):
    """ Base class for shared behavior between trigger and criteria. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, d):
        pass

    @abc.abstractmethod
    def matches(self, msg):
        pass


class Trigger(BaseComparator):

    def __init__(self, d):
        self._d = d

    def matches(self, msg):
        for k, v in self._d.items():
            if not msg[k] is v:
                return False
        return True


class Criteria(BaseComparator):

    def __init__(self, d):
        self._d = d

    def matches(self, msg):
        raise NotImplementedError("need to write this")
