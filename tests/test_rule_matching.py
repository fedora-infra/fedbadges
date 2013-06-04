import unittest

import fedbadges.models

from mock import patch
from nose.tools import eq_, raises


class TestRuleMatching(unittest.TestCase):

    @raises(ValueError)
    def test_metadata_validation(self):
        """ Test for failure if not enough metadata """
        rule = fedbadges.models.BadgeRule(dict(name="Test"), None)

    @raises(ValueError)
    def test_full_specification(self):
        """ Test for failure if no criteria specified. """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(topic="test_topic"),
        ), None)


    def test_full_simple_success(self):
        """ A simple integration test for messages with zero users """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="bodhi"),
            criteria=dict(datanommer=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
                condition={"greater than or equal to": 1}
            ))
        ), None)

        msg = _example_real_bodhi_message

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, query
            eq_(rule.matches(msg), set(['hadess']))

    def test_full_simple_match_almost_succeed(self):
        """ A simple integration test for messages with zero users """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="bodhi"),
            criteria=dict(datanommer=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
                condition={"greater than or equal to": 1}
            ))
        ), None)

        # This message has zero users associated with it, so even if trigger
        # and criteria are met, there's noone to award the badge to -- and so,
        # we should *fail* the ``matches`` call.
        msg = {
            'topic': "org.fedoraproject.prod.bodhi.mashtask.complete",
            'msg': {'success': False}
        }

        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, query
            eq_(rule.matches(msg), set())

    def test_yaml_specified_awardee_success(self):
        """ Test that when we can override msg2usernames. """
        # For instance, fas.group.member.remove contains two users,
        # the one being removed from a group, and the one doing the removing.
        # a badge YAML definition needs to be able to specify *which* of these
        # two users should receive its badge.  The dotted substitution
        # notation should suffice for this.  If this is specified, use it.
        # If not, use fedmsg.meta.msg2usernames for convenience.  It will do
        # in most all cases.

        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="fas"),
            criteria=dict(datanommer=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
                condition={"greater than or equal to": 1}
            )),
            recipient="msg.agent.username",
        ), None)

        msg = {
            u'topic': u'org.fedoraproject.stg.fas.role.update',
            u'msg': {
                u'group': {u'name': u'ambassadors'},
                u'user': {u'username': u'ralph'},
                u'agent': {u'username': u'toshio'},
            }
        }


        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, query
            eq_(rule.matches(msg), set(['toshio']))

    def test_yaml_specified_awardee_failure(self):
        """ Test that when we don't override msg2usernames, we get 2 awardees.
        """
        rule = fedbadges.models.BadgeRule(dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="fas"),
            criteria=dict(datanommer=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
                condition={"greater than or equal to": 1}
            ))
        ), None)

        msg = {
            u'topic': u'org.fedoraproject.stg.fas.role.update',
            u'msg': {
                u'group': {u'name': u'ambassadors'},
                u'user': {u'username': u'ralph'},
                u'agent': {u'username': u'toshio'},
            }
        }


        class MockQuery(object):
            def count(self):
                return 1

        query = MockQuery()

        with patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, query
            eq_(rule.matches(msg), set(['toshio', 'ralph']))


_example_real_bodhi_message = {
    "topic": "org.fedoraproject.prod.bodhi.update.request.testing",
    "msg": {
        'agent': 'lmacken',
        "update": {
            "status": "pending",
            "critpath": False,
            "stable_karma": 3,
            "date_pushed": None,
            "title": "gnome-settings-daemon-3.6.1-1.fc18," +
            "control-center-3.6.1-1.fc18",
            "nagged": None,
            "comments": [
            {
                "group": None,
                "author": "bodhi",
                "text": "This update has been submitted for "
                "testing by hadess. ",
                "karma": 0,
                "anonymous": False,
                "timestamp": 1349718539.0,
                "update_title": "gnome-settings-daemon-3.6.1-1.fc18," +
                "control-center-3.6.1-1.fc18"
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
                "id_prefix": "FEDORA"
            },
            "approved": None,
            "builds": [
            {
                "nvr": "gnome-settings-daemon-3.6.1-1.fc18",
                "package": {
                    "suggest_reboot": False,
                    "committers": [
                        "hadess",
                        "ofourdan",
                        "mkasik",
                        "cosimoc"
                    ],
                    "name": "gnome-settings-daemon"
                }
            }, {
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
                        "rstrode"
                    ],
                    "name": "control-center"
                }
            }
            ],
            "date_modified": None,
            "notes": "This update fixes numerous bugs in the new Input " +
            "Sources support, the Network panel and adds a help " +
            "screen accessible via Wacom tablets's buttons.",
            "request": "testing",
            "bugs": [],
            "critpath_approved": False,
            "karma": 0,
            "submitter": "hadess"
        }
    },
    "i": 2,
    "timestamp": 1349718539.0,
}
