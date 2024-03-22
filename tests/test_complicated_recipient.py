import unittest
import logging

import fedbadges.consumers

from mock import patch, Mock
from nose.tools import eq_

from io import StringIO

# Utils for tests
from . import utils


class TestComplicatedRecipient(unittest.TestCase):

    @patch("fedmsg.init")
    @patch("badgrclient.BadgrClient._get_auth_token")
    @patch("badgrclient.BadgrClient._call_api")
    @patch("badgrclient.Issuer.create")
    @patch("badgrclient.BadgeClass.create")
    def setUp(self, fedmsg_init, _get_auth_token, _call_api, create_issuer, create_badge):
        hub = utils.MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)

    @patch("datanommer.models.Message.grep")
    @patch("badgrclient.BadgeClass.fetch_assertions")
    def test_complicated_recipient_real(
        self,
        fetch_assertions,
        grep,
    ):

        for rule in self.consumer.badge_rules:
            if rule["name"] == "Speak Up!":
                self.rule = rule
        msg = {
            "username": "daemon",
            "i": 236,
            "timestamp": 1372103541.190249,
            "topic": "org.fedoraproject.prod.meetbot.meeting.complete",
            "msg": {
                "meeting_topic": "testing",
                "attendees": {"zodbot": 2, "threebean": 2},
                "chairs": {},
                "topic": "",
                "url": "fedora-meeting.2013-06-24-19.52",
                "owner": "threebean",
                "channel": "#fedora-meeting",
            },
        }

        # Set up some mock stuff
        class MockQuery(object):
            def count(self):
                return float("inf")  # Master tagger

        grep.return_value = float("inf"), 1, MockQuery()
        fetch_assertions.return_value = []

        with patch("fedbadges.rules.user_exists_in_fas") as g:
            g.return_value = True
            eq_(self.rule.matches(msg), set(["zodbot", "threebean"]))

    @patch("datanommer.models.Message.grep")
    @patch("badgrclient.BadgeClass.fetch_assertions")
    def test_complicated_recipient_pagure(
        self,
        fetch_assertions,
        grep,
    ):

        for rule in self.consumer.badge_rules:
            if rule["name"] == "Long Life to Pagure (Pagure I)":
                self.rule = rule
        msg = {
            "username": "git",
            "source_name": "datanommer",
            "i": 1,
            "timestamp": 1528825180.0,
            "topic": "io.pagure.prod.pagure.git.receive",
            "msg": {
                "authors": [
                    {"fullname": "Pierre-YvesChibon", "name": "pingou"},
                    {"fullname": "Lubom\\u00edr Sedl\\u00e1\\u0159", "name": "lsedlar"},
                ],
                "total_commits": 2,
                "start_commit": "da090b8449237e3878d4d1fe56f7f8fcfd13a248",
            },
        }

        # Set up some mock stuff
        class MockQuery(object):
            def count(self):
                return float("inf")  # Master tagger

        grep.return_value = float("inf"), 1, MockQuery()
        fetch_assertions.return_value = []

        with patch("fedbadges.rules.user_exists_in_fas") as g:
            g.return_value = True
            eq_(self.rule.matches(msg), set(["pingou", "lsedlar"]))

    @patch("datanommer.models.Message.grep")
    @patch("badgrclient.BadgeClass.fetch_assertions")
    def test_complicated_recipient_pagure_bad(
        self,
        fetch_assertions,
        grep,
    ):

        for rule in self.consumer.badge_rules:
            if rule["name"] == "Long Life to Pagure (Pagure I)":
                self.rule = rule
        msg = {
            "username": "git",
            "source_name": "datanommer",
            "i": 1,
            "timestamp": 1528825180.0,
            "topic": "io.pagure.prod.pagure.git.receive",
            "msg": {
                "authors": [
                    {
                        "fullname": "Pierre-YvesChibon",
                    },
                    {
                        "fullname": "Lubom\\u00edr Sedl\\u00e1\\u0159",
                    },
                ],
                "total_commits": 2,
                "start_commit": "da090b8449237e3878d4d1fe56f7f8fcfd13a248",
            },
        }

        # Set up some mock stuff
        class MockQuery(object):
            def count(self):
                return float("inf")  # Master tagger

        grep.return_value = float("inf"), 1, MockQuery()
        fetch_assertions.return_value = []

        with patch("fedbadges.rules.user_exists_in_fas") as g:
            g.return_value = True
            self.assertRaises(Exception, "Multiple recipients : name not found in the message")
