import unittest

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch
from nose.tools import eq_


class MockHub(object):
    config = {
        "fedmsg.consumers.badges.enabled": True,
        "badges.yaml.directory": "tests/test_badges",
        "badges_global": {
            "database_uri": "sqlite:////tmp/sqlite.db",
            "badge_issuer": dict(
                issuer_id='Fedora Project',
                issuer_origin='http://badges.fedoraproject.com',
                issuer_name='Fedora Project',
                issuer_org='http://fedoraproject.org',
                issuer_contact='rdelinge@redhat.com'
            ),
        },
        "datanommer.sqlalchemy.url": "sqlite://",
    }

    def subscribe(self, topic, callback):
        pass


class TestYamlCollector(unittest.TestCase):

    @patch('tahrir_api.dbapi.TahrirDatabase.add_issuer')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_badge')
    def setUp(self, add_issuer, add_badge):
        hub = MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)

    def test_load_badges_number(self):
        """ Determine that we can load badges from file. """
        eq_(len(self.consumer.badge_rules), 2)

    def test_load_badges_contents(self):
        """ Determine that we can load badges from file. """
        names = set([badge['name'] for badge in self.consumer.badge_rules])
        eq_(names, set([
            'Like a Rock',
            'The Zen of Foo Bar Baz',
            ]))
