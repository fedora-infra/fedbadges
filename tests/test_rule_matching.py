import unittest

import fedbadges.rules

from mock import patch, Mock
from nose.tools import eq_, raises


class TestRuleMatching(unittest.TestCase):

    @raises(ValueError)
    def test_metadata_validation(self):
        """Test for failure if not enough metadata"""
        rule = fedbadges.rules.BadgeRule(dict(name="Test"), None, None)

    @raises(ValueError)
    def test_full_specification(self):
        """Test for failure if no criteria specified."""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(topic="test_topic"),
            ),
            None,
            None,
        )

    def test_full_simple_success(self):
        """A simple integration test for messages with zero users"""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="bodhi"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
            ),
            None,
            None,
        )

        msg = _example_real_bodhi_message

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, query
            with patch("fedbadges.rules.user_exists_in_fas") as g:
                g.return_value = True
                eq_(rule.matches(msg), set(["lmacken", "hadess"]))

    def test_full_simple_match_almost_succeed(self):
        """A simple integration test for messages with zero users"""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="bodhi"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
            ),
            None,
            None,
        )

        # This message has zero users associated with it, so even if trigger
        # and criteria are met, there's noone to award the badge to -- and so,
        # we should *fail* the ``matches`` call.
        msg = {"topic": "org.fedoraproject.prod.bodhi.mashtask.complete", "msg": {"success": False}}

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, query
            eq_(rule.matches(msg), set())

    def test_yaml_specified_awardee_success(self):
        """Test that we can override msg2usernames."""
        # For instance, fas.group.member.remove contains two users,
        # the one being removed from a group, and the one doing the removing.
        # a badge YAML definition needs to be able to specify *which* of these
        # two users should receive its badge.  The dotted substitution
        # notation should suffice for this.  If this is specified, use it.
        # If not, use fedmsg.meta.msg2usernames for convenience.  It will do
        # in most all cases.

        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="fas"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
                recipient="%(msg.agent.username)s",
            ),
            None,
            None,
        )

        msg = {
            "topic": "org.fedoraproject.stg.fas.role.update",
            "msg": {
                "group": {"name": "ambassadors"},
                "user": {"username": "ralph"},
                "agent": {"username": "toshio"},
            },
        }

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, query
            with patch("fedbadges.rules.user_exists_in_fas") as g:
                g.return_value = True
                eq_(rule.matches(msg), set(["toshio"]))

    def test_yaml_specified_awardee_failure(self):
        """Test that when we don't override msg2usernames, we get 2 awardees."""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="fas"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
            ),
            None,
            None,
        )

        msg = {
            "topic": "org.fedoraproject.stg.fas.role.update",
            "msg": {
                "group": {"name": "ambassadors"},
                "user": {"username": "ralph"},
                "agent": {"username": "toshio"},
            },
        }

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, query
            with patch("fedbadges.rules.user_exists_in_fas") as g:
                g.return_value = True
                eq_(rule.matches(msg), set(["toshio", "ralph"]))

    @patch("badgrclient.BadgeClass.create")
    @patch("badgrclient.BadgeClass.fetch_assertions")
    def test_against_duplicates(self, fetch_assertions, badgeclass_create):
        """Test that matching fails if user already has the badge."""

        def mock_fetch_assertions(recipient):
            if recipient["identity"] == "toshio@fedoraproject.org":
                return [1]
            return []

        fetch_assertions.side_effect = mock_fetch_assertions

        class MockBadgrClient(object):
            unique_badge_names = True

            def get_eid_from_badge_name(self, badgr_name, issuer_id):
                return "randomid"

        badgr_client = MockBadgrClient()

        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="fas"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
            ),
            badgr_client,
            None,
        )

        msg = {
            "topic": "org.fedoraproject.stg.fas.role.update",
            "msg": {
                "group": {"name": "ambassadors"},
                "user": {"username": "ralph"},
                "agent": {"username": "toshio"},
            },
        }

        class MockDatanommerQuery(object):
            def count(self):
                return 1

        datanommer_query = MockDatanommerQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, datanommer_query
            with patch("fedbadges.rules.user_exists_in_fas") as g:
                g.return_value = True
                eq_(rule.matches(msg), set(["ralph"]))

    @patch.dict(
        fedbadges.rules.fedmsg_config,
        {
            "keytab": "/etc/krb5.keytab",
            "fasjson_base_url": "https://fasjson.example.com/v1/",
        },
    )
    @patch("fedbadges.rules.user_exists_in_fas", Mock(return_value=True))
    def test_github_awardee(self):
        """Conversion from GitHub URI to FAS users"""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="bodhi"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
                recipient="%(msg.user)s",
                recipient_github2fas="Yes",
            ),
            None,
            None,
        )

        msg = {
            "topic": "org.fedoraproject.prod.bodhi.update.request.testing",
            "msg": {"user": "https://api.github.com/users/dummygh"},
        }

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, query
            with patch("fedbadges.utils.requests") as req:
                session = req.Session.return_value = Mock()
                response = session.get.return_value = Mock()
                response.json.return_value = {
                    "result": [{"username": "dummy"}],
                    "page": {"total_results": 1},
                }
                eq_(rule.matches(msg), set(["dummy"]))

    def test_krb_awardee(self):
        """Conversion from Kerberos user to FAS users"""
        rule = fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
                trigger=dict(category="buildsys"),
                criteria=dict(
                    datanommer=dict(
                        filter=dict(categories=["pkgdb"]),
                        operation="count",
                        condition={"greater than or equal to": 1},
                    )
                ),
                recipient="%(msg.owner)s",
                recipient_krb2fas="Yes",
            ),
            None,
            None,
        )

        msg = {
            "msg_id": "cedd7ab4-8a59-4704-bd1b-0e7297bf759c",
            "topic": "org.fedoraproject.prod.buildsys.build.state.change",
            "headers": {
                "fedora_messaging_severity": 20,
                "sent-at": "2022-06-29T16:27:05+00:00",
                "fedora_messaging_schema": "base.message",
            },
            "msg": {
                "build_id": 1994993,
                "old": 0,
                "name": "dummy-test-package-gloster",
                "task_id": 88890394,
                "instance": "primary",
                "attribute": "state",
                "request": [
                    "git+https://src.fedoraproject.org/rpms/dummy-test-package-gloster.git#aaf707bc5671ab5e00c5618d95bfd83803ca54c0",
                    "rawhide",
                    {},
                ],
                "owner": "packagerbot/os-master02.iad2.fedoraproject.org",
                "epoch": None,
                "version": "0",
                "release": "9242.fc37",
                "new": 1,
            },
        }
        msg = {
            "topic": "org.fedoraproject.prod.buildsys.build.state.change",
            "msg": {"owner": "packagerbot/os-master02.iad2.fedoraproject.org"},
        }

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = 1, 1, query
            with patch("fedbadges.rules.user_exists_in_fas") as g:
                g.return_value = True
                eq_(rule.matches(msg), set(["packagerbot"]))


_example_real_bodhi_message = {
    "topic": "org.fedoraproject.prod.bodhi.update.request.testing",
    "msg": {
        "agent": "lmacken",
        "update": {
            "status": "pending",
            "critpath": False,
            "stable_karma": 3,
            "date_pushed": None,
            "title": "gnome-settings-daemon-3.6.1-1.fc18," + "control-center-3.6.1-1.fc18",
            "nagged": None,
            "comments": [
                {
                    "group": None,
                    "author": "bodhi",
                    "text": "This update has been submitted for " "testing by hadess. ",
                    "karma": 0,
                    "anonymous": False,
                    "timestamp": 1349718539.0,
                    "update_title": "gnome-settings-daemon-3.6.1-1.fc18,"
                    + "control-center-3.6.1-1.fc18",
                }
            ],
            "updateid": None,
            "type": "bugfix",
            "close_bugs": True,
            "date_submitted": 1349718534.0,
            "unstable_karma": -3,
            "release": {
                "dist_tag": "f18",
                "locked": True,
                "long_name": "Fedora 18",
                "name": "F18",
                "id_prefix": "FEDORA",
            },
            "approved": None,
            "builds": [
                {
                    "nvr": "gnome-settings-daemon-3.6.1-1.fc18",
                    "package": {
                        "suggest_reboot": False,
                        "committers": ["hadess", "ofourdan", "mkasik", "cosimoc"],
                        "name": "gnome-settings-daemon",
                    },
                },
                {
                    "nvr": "control-center-3.6.1-1.fc18",
                    "package": {
                        "suggest_reboot": False,
                        "committers": [
                            "ctrl-center-team",
                            "ofourdan",
                            "ssp",
                            "ajax",
                            "alexl",
                            "jrb",
                            "mbarnes",
                            "caolanm",
                            "davidz",
                            "mclasen",
                            "rhughes",
                            "hadess",
                            "johnp",
                            "caillon",
                            "whot",
                            "rstrode",
                        ],
                        "name": "control-center",
                    },
                },
            ],
            "date_modified": None,
            "notes": "This update fixes numerous bugs in the new Input "
            + "Sources support, the Network panel and adds a help "
            + "screen accessible via Wacom tablets's buttons.",
            "request": "testing",
            "bugs": [],
            "critpath_approved": False,
            "karma": 0,
            "submitter": "hadess",
        },
    },
    "i": 2,
    "timestamp": 1349718539.0,
}
