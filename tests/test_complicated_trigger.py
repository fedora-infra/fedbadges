import unittest
import logging

import fedbadges.consumers

from mock import patch, Mock
from nose.tools import eq_

from io import StringIO

# Utils for tests
from . import utils


class TestComplicatedTrigger(unittest.TestCase):

    @patch("fedmsg.init")
    @patch("badgrclient.BadgrClient._get_auth_token")
    @patch("badgrclient.BadgrClient._call_api")
    @patch("badgrclient.Issuer.create")
    @patch("badgrclient.BadgeClass.create")
    def setUp(self, create_badge, create_issuer, _call_api, _get_auth_token, fedmsg_init):
        hub = utils.MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)
        for rule in self.consumer.badge_rules:
            if rule["name"] == "Junior Tagger (Tagger I)":
                self.rule = rule

    def test_complicated_trigger_against_empty(self):
        msg = {
            "topic": "org.fedoraproject.prod.fedoratagger.tag.create",
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_one(self):
        msg = {
            "topic": "org.fedoraproject.prod.fedoratagger.tag.create",
            "msg": {},
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_two(self):
        msg = {
            "topic": "org.fedoraproject.prod.fedoratagger.tag.create",
            "msg": {"user": {}},
        }
        eq_(self.rule.matches(msg), set())

    def test_complicated_trigger_against_partial_mismatch(self):
        msg = {
            "topic": "org.fedoraproject.prod.fedoratagger.tag.create",
            "msg": {"user": None},
        }

        log = logging.getLogger("moksha.hub")
        log.error = Mock()
        eq_(self.rule.matches(msg), set())
        log.error.assert_called()

    @patch("datanommer.models.Message.grep")
    @patch("badgrclient.BadgeClass.fetch_assertions")
    def test_complicated_trigger_against_full_match(
        self,
        fetch_assertions,
        grep,
    ):
        msg = {
            "i": 2,
            "msg": {
                "tag": {
                    "dislike": 0,
                    "like": 1,
                    "package": "mattd",
                    "tag": "awesome",
                    "total": 1,
                    "votes": 1,
                },
                "user": {"anonymous": False, "rank": -1, "username": "ralph", "votes": 4},
                "vote": {
                    "like": True,
                    "tag": {
                        "dislike": 0,
                        "like": 1,
                        "package": "mattd",
                        "tag": "awesome",
                        "total": 1,
                        "votes": 1,
                    },
                    "user": {"anonymous": False, "rank": -1, "username": "ralph", "votes": 4},
                },
            },
            "timestamp": 1365444411.924043,
            "topic": "org.fedoraproject.prod.fedoratagger.tag.create",
            "username": "threebean",
        }

        # Set up some mock stuff
        class MockQuery(object):
            def count(self):
                return float("inf")  # Master tagger

        grep.return_value = float("inf"), 1, MockQuery()
        fetch_assertions.return_value = []

        with patch("fedbadges.rules.user_exists_in_fas") as g:
            g.return_value = True
            eq_(self.rule.matches(msg), set(["ralph"]))
