import unittest

import badgrclient
import fedbadges.consumers

from mock import patch
from nose.tools import eq_

# Utils for tests
from .utils import MockHub


class TestYamlCollector(unittest.TestCase):

    @patch("fedmsg.init")
    @patch("badgrclient.BadgrClient._get_auth_token")
    @patch("badgrclient.BadgrClient._call_api")
    @patch("badgrclient.Issuer.create")
    @patch("badgrclient.BadgeClass.create")
    def setUp(self, create_badge, create_issuer, _call_api, _get_auth_token, fedmsg_init):
        hub = MockHub()
        self.consumer = fedbadges.consumers.FedoraBadgesConsumer(hub)

    def test_load_badges_number(self):
        """Determine that we can load badges from file."""
        eq_(len(self.consumer.badge_rules), 5)

    def test_load_badges_contents(self):
        """Determine that we can load badges from file."""
        names = set([badge["name"] for badge in self.consumer.badge_rules])
        eq_(
            names,
            set(
                [
                    "Like a Rock",
                    "The Zen of Foo Bar Baz",
                    "Junior Tagger (Tagger I)",
                    "Speak Up!",
                    "Long Life to Pagure (Pagure I)",
                ]
            ),
        )
