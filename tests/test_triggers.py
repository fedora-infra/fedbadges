import unittest

from nose.tools import raises

import fedbadges.models


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
