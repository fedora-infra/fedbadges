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

    # TODO test integrated trigger and criteria matching


class TestTriggerMatching(unittest.TestCase):
    def test_basic_topic_matching_isolated(self):
        """ Test that the matches method can match a basic topic. """
        trigger = fedbadges.models.Trigger(dict(
            topic="test_topic",
        ))
        message = dict(
            topic="test_topic",
        )
        assert(trigger.matches(message))

    @raises(ValueError)
    def test_malformed_trigger(self):
        trigger = fedbadges.models.Trigger(dict(
            watwat="does not exist",
        ))

    # TODO test that matches is false if user already has the badge.


class TestCriteriaMatching(unittest.TestCase):
    @raises(ValueError)
    def test_malformed_criteria(self):
        criteria = fedbadges.models.Criteria(dict(
            watwat="does not exist",
        ))

    # TODO - mock out datanommer to test real criteria
