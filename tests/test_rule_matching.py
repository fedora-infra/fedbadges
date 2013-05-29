import unittest

import fedbadges.models

from mock import patch
from nose.tools import eq_, raises


class TestRuleMatching(unittest.TestCase):

    def setUp(self):
        pass


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


    def test_basic_topic_matching(self):
        """ Test that the matches method can match a basic topic. """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            trigger=dict(topic="test_topic"),
            criteria=dict(),
        ))
        message = dict(
            topic="test_topic",
        )
        assert(rule.matches(message))

    # TODO test malformed trigger
    # TODO test malformed criteria
