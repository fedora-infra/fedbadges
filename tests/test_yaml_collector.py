import unittest

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch
from nose.tools import eq_

# Utils for tests
import utils


class TestYamlCollector(unittest.TestCase):

    @patch('fedmsg.init')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_issuer')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_badge')
    def setUp(self, fedmsg_init, add_issuer, add_badge):
        hub = utils.MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)

    def test_load_badges_number(self):
        """ Determine that we can load badges from file. """
        eq_(len(self.consumer.badge_rules), 5)

    def test_load_badges_contents(self):
        """ Determine that we can load badges from file. """
        names = set([badge['name'] for badge in self.consumer.badge_rules])
        eq_(names, set([
            'Like a Rock',
            'The Zen of Foo Bar Baz',
            'Junior Tagger (Tagger I)',
            'Speak Up!',
            'Long Life to Pagure (Pagure I)',
            ]))
