import unittest

import fedbadges.models

from mock import patch
from nose.tools import eq_, raises


class TestRuleMatching(unittest.TestCase):

    @raises(ValueError)
    def test_metadata_validation(self):
        """ Test for failure if not enough metadata """
        rule = fedbadges.models.BadgeRule(dict(name="Test"))

    @raises(ValueError)
    def test_full_specification(self):
        """ Test for failure if no criteria specified. """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            trigger=dict(topic="test_topic"),
        ))

    # TODO test integrated trigger and criteria matching
    # TODO test that matches is false if user already has the badge.
