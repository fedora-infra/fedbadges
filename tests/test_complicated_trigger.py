import unittest
import logging

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch, Mock
from nose.tools import eq_

from StringIO import StringIO

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

        log = logging.getLogger('moksha.hub')
        log.error = Mock()
        eq_(self.rule.matches(msg), set())
        log.error.assert_called()

    @patch('datanommer.models.Message.grep')
    @patch('tahrir_api.dbapi.TahrirDatabase.get_person')
    @patch('tahrir_api.dbapi.TahrirDatabase.assertion_exists')
    def test_complicated_trigger_against_full_match(self,
                                                    assertion_exists,
                                                    get_person,
                                                    grep,
                                                    ):
        msg = {
            'i': 2,
            'msg': {
                'tag': {
                    'dislike': 0,
                    'like': 1,
                    'package': 'mattd',
                    'tag': 'awesome',
                    'total': 1,
                    'votes': 1},
                'user': {
                    'anonymous': False,
                    'rank': -1,
                    'username': 'ralph',
                    'votes': 4},
                'vote': {
                    'like': True,
                    'tag': {
                        'dislike': 0,
                        'like': 1,
                        'package': 'mattd',
                        'tag': 'awesome',
                        'total': 1,
                        'votes': 1},
                    'user': {
                        'anonymous': False,
                        'rank': -1,
                        'username': 'ralph',
                        'votes': 4}}},
            'timestamp': 1365444411.924043,
            'topic': 'org.fedoraproject.prod.fedoratagger.tag.create',
            'username': 'threebean'}

        # Set up some mock stuff
        class MockQuery(object):
            def count(self):
                return float("inf")  # Master tagger

        class MockPerson(object):
            opt_out = False

        grep.return_value = float("inf"), 1, MockQuery()
        get_person.return_value = MockPerson()
        assertion_exists.return_value = False

        with patch("fedbadges.rules.user_exists_in_fas") as g:
            g.return_value = True
            eq_(self.rule.matches(msg), set(['ralph']))
