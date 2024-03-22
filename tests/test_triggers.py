import unittest

from nose.tools import raises

import fedbadges.rules


class TestTriggerMatching(unittest.TestCase):
    def test_basic_topic_matching_isolated(self):
        """Test that the matches method can match a basic topic."""
        trigger = fedbadges.rules.Trigger(
            dict(
                topic="test_topic",
            )
        )
        message = dict(
            topic="test_topic",
        )
        assert trigger.matches(message)

    def test_basic_category_matching_isolated(self):
        """Test that the matches method can match a basic category."""
        trigger = fedbadges.rules.Trigger(
            dict(
                category="test_category",
            )
        )
        message = dict(
            topic="org.fedoraproject.dev.test_category.some_topic",
        )
        assert trigger.matches(message)

    def test_basic_conjunction_pass(self):
        """Test that two anded fields accept the right message"""
        trigger = fedbadges.rules.Trigger(
            {
                "all": [
                    dict(topic="org.fedoraproject.dev.test_category.test_topic"),
                    dict(category="test_category"),
                ]
            }
        )
        message = dict(
            topic="org.fedoraproject.dev.test_category.test_topic",
        )
        assert trigger.matches(message)

    def test_basic_conjunction_fail(self):
        """Test that two anded fields reject non-matching messages"""
        trigger = fedbadges.rules.Trigger(
            {
                "all": [
                    dict(topic="org.fedoraproject.dev.test_category.test_topic"),
                    dict(category="test_category"),
                ]
            }
        )
        message = dict(
            topic="org.fedoraproject.dev.test_category.test_topic.doesntmatch",
        )
        assert not trigger.matches(message)

    def test_lambdas_pass(self):
        """Test that lambdas match correctly"""
        trigger = fedbadges.rules.Trigger(
            {
                "lambda": "'s3kr3t' in json.dumps(msg)",
            }
        )
        message = dict(msg=dict(nested=dict(something="s3kr3t")))
        assert trigger.matches(message)

    def test_lambdas_fail(self):
        """Test that lambdas fail correctly"""
        trigger = fedbadges.rules.Trigger(
            {
                "lambda": "'one string' in json.dumps(msg)",
            }
        )
        message = dict(msg=dict(nested=dict(something="another string")))
        assert not trigger.matches(message)

    @raises(TypeError)
    def test_invalid_nesting(self):
        """Test that invalid nesting is detected and excepted."""
        trigger = fedbadges.rules.Trigger(
            {
                "all": dict(
                    topic="org.fedoraproject.dev.test_category.test_topic",
                    category="test_category",
                )
            }
        )

    @raises(ValueError)
    def test_two_fields(self):
        """Test that passing two statements as a trigger is invalid."""
        trigger = fedbadges.rules.Trigger(
            dict(
                topic="test_topic",
                category="test_topic",
            )
        )

    @raises(KeyError)
    def test_malformed_trigger(self):
        """Test that a single, undefined field is handled as invalid."""
        trigger = fedbadges.rules.Trigger(
            dict(
                watwat="does not exist",
            )
        )
