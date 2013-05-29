# -*- coding; utf-8 -*-
""" Models for fedbadges.

The primary thing here is a "BadgeRule" which is an in-memory working
abstraction of the trigger and criteria required to award a badge.

Authors:    Ralph Bean
"""

class BadgeRule(object):

    def __init__(self, badge_dict):
        self._d = badge_dict

    def __getitem__(self, key):
        return self._d[key]

    def matches(self, msg):
        raise NotImplementedError("I haven't written this yet.")

