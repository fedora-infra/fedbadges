import unittest
import fedbadges.consumers.yamlconsumer

from nose.tools import eq_

class MockHub(object):
    config = {
        "badges.yaml.directory": "tests/test_badges",
    }

class TestYamlCollector(unittest.TestCase):

    def test_load_badges_number(self):
        """ Determine that we can load badges from file. """

        hub = MockHub()
        consumer = fedbadges.consumers.yamlconsumer.YAMLConsumer(hub)
        eq_(len(consumer.badges), 2)
