import unittest

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch
from nose.tools import eq_

# Utils for tests
import utils


class TestComplicatedTrigger(unittest.TestCase):

    @patch('fedmsg.init')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_issuer')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_badge')
    def setUp(self, fedmsg_init, add_issuer, add_badge):
        hub = utils.MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)
        for rule in self.consumer.badge_rules:
            if rule['name'] == 'Junior Tagger (Tagger I)':
                self.rule = rule


    def test_complicated_trigger_against_empty(self):
        msg = {
            'topic': 'org.fedoraproject.prod.fedoratagger.tag.create',
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_one(self):
        msg = {
            'topic': 'org.fedoraproject.prod.fedoratagger.tag.create',
            'msg': {},
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_two(self):
        msg = {
            'topic': 'org.fedoraproject.prod.fedoratagger.tag.create',
            'msg': {
                'user': {}
            },
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_mismatch(self):
        msg = {
            'topic': 'org.fedoraproject.prod.fedoratagger.tag.create',
            'msg': {
                'user': None
            },
        }
        eq_(self.rule.matches(msg), set())
