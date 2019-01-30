import unittest
import logging

import tahrir_api.dbapi
import fedbadges.consumers

from mock import patch, Mock
from nose.tools import eq_

from io import StringIO

# Utils for tests
from . import utils


class TestComplicatedRecipient(unittest.TestCase):

    @patch('fedmsg.init')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_issuer')
    @patch('tahrir_api.dbapi.TahrirDatabase.add_badge')
    def setUp(self, fedmsg_init, add_issuer, add_badge):
        hub = utils.MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)
        for rule in self.consumer.badge_rules:
            if rule['name'] == 'Speak Up!':
                self.rule = rule

    @patch('datanommer.models.Message.grep')
    @patch('tahrir_api.dbapi.TahrirDatabase.get_person')
    @patch('tahrir_api.dbapi.TahrirDatabase.assertion_exists')
    def test_complicated_recipient_real(self,
                                        assertion_exists,
                                        get_person,
                                        grep,
                                        ):
        msg = {
            'username': 'daemon',
            'i': 236,
            'timestamp': 1372103541.190249,
            'topic': 'org.fedoraproject.prod.meetbot.meeting.complete',
            'msg': {
                'meeting_topic': 'testing',
                'attendees': {'zodbot': 2,
                               'threebean': 2},
                'chairs': {},
                'topic': '',
                'url': 'fedora-meeting.2013-06-24-19.52',
                'owner': 'threebean',
                'channel': '#fedora-meeting'
            }
        }

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
            eq_(self.rule.matches(msg), set(['zodbot', 'threebean']))
