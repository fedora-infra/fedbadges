from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fedora_messaging.message import Message
from noggin_messages import MemberSponsorV1

import fedbadges.rules

from .utils import example_real_bodhi_message


class MockQuery:
    def count():
        return 1


@pytest.fixture
def user_exists(fasjson_client):
    fasjson_client.get_user.return_value = SimpleNamespace(result={"username": "dummy-user"})


def test_metadata_validation():
    """Test for failure if not enough metadata"""
    with pytest.raises(ValueError):
        fedbadges.rules.BadgeRule(dict(name="Test"), None, None, None)


def test_full_specification():
    """Test for failure if no trigger is specified."""
    with pytest.raises(ValueError):
        fedbadges.rules.BadgeRule(
            dict(
                name="Test",
                description="Doesn't matter...",
                creator="Somebody",
                discussion="http://somelink.com",
                issuer_id="fedora-project",
                image_url="http://somelinke.com/something.png",
            ),
            1,
            None,
            None,
        )


def test_full_simple_success(fasproxy, tahrir_client, fm_config, user_exists):
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
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    msg = example_real_bodhi_message

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == {"lmacken"}


def test_full_simple_match_almost_succeed(fasproxy, tahrir_client, fm_config):
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
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    # This message has zero users associated with it, so even if trigger
    # and condition are met, there's noone to award the badge to -- and so,
    # we should *fail* the ``matches`` call.
    msg = Message(topic="org.fedoraproject.prod.bodhi.mashtask.complete", body={"success": False})

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 0
        assert rule.matches(msg, tahrir_client) == set()


def test_skip_user(fasproxy, tahrir_client, fm_config, user_exists):
    """Test that skipped users are actually skipped."""
    rule = fedbadges.rules.BadgeRule(
        dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="fas"),
            condition={"greater than or equal to": 1},
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    msg = MemberSponsorV1(
        topic="org.fedoraproject.stg.fas.group.member.sponsor",
        body={
            "msg": {
                "group": "ambassadors",
                "user": "ralph",
                "agent": "toshio",
            }
        },
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == frozenset(["toshio"])
        get_current_value.assert_called_once()
        get_current_value.reset_mock()
        # Now add Toshio to the skipped users
        rule.config["skip_users"] = ["toshio"]
        assert rule.matches(msg, tahrir_client) == frozenset()
        get_current_value.assert_not_called()


def test_yaml_specified_awardee_success(fasproxy, tahrir_client, fm_config, user_exists):
    """Test that we can override msg.usernames."""
    # For instance, fas.group.member.remove contains two users,
    # the one being removed from a group, and the one doing the removing.
    # a badge YAML definition needs to be able to specify *which* of these
    # two users should receive its badge.  The dotted substitution
    # notation should suffice for this.  If this is specified, use it.
    # If not, use msg.usernames for convenience.  It will do
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
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
            recipient="[message.body['agent']['username'], message.body['user']['username']]",
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    msg = Message(
        topic="org.fedoraproject.stg.fas.role.update",
        body={
            "group": {"name": "ambassadors"},
            "user": {"username": "ralph"},
            "agent": {"username": "toshio"},
        },
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == {"toshio", "ralph"}


def test_yaml_specified_awardee_failure(fasproxy, tahrir_client, fm_config, user_exists):
    """Test that when we don't override msg.usernames, we get 2 awardees."""
    rule = fedbadges.rules.BadgeRule(
        dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="fas"),
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    msg = MemberSponsorV1(
        topic="org.fedoraproject.stg.fas.group.member.sponsor",
        body={
            "msg": {
                "group": "ambassadors",
                "user": "ralph",
                "agent": "toshio",
            }
        },
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == {"toshio"}


def test_against_duplicates(fasproxy, tahrir_client, fm_config, user_exists):
    """Test that matching fails if user already has the badge."""

    rule = fedbadges.rules.BadgeRule(
        dict(
            name="Test",
            description="Doesn't matter...",
            creator="Somebody",
            discussion="http://somelink.com",
            issuer_id="fedora-project",
            image_url="http://somelinke.com/something.png",
            trigger=dict(category="fas"),
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
            recipient="message.usernames",
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)
    tahrir_client.add_person("toshio@fedoraproject.org")
    tahrir_client.session.commit()
    tahrir_client.add_assertion(rule.badge_id, "toshio@fedoraproject.org", None, None)
    tahrir_client.session.commit()
    print(tahrir_client.assertion_exists(rule.badge_id, "toshio@fedoraproject.org"))
    print(rule.badge_id)

    msg = MemberSponsorV1(
        topic="org.fedoraproject.stg.fas.group.member.sponsor",
        body={
            "msg": {
                "group": "ambassadors",
                "user": "ralph",
                "agent": "toshio",
            }
        },
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == set(["ralph"])


def test_github_awardee(fasproxy, tahrir_client, fasjson_client, fm_config, user_exists):
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
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
            recipient="message.body['user']",
            recipient_github2fas="Yes",
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    msg = Message(
        topic="org.fedoraproject.prod.bodhi.update.request.testing",
        body={"user": "https://api.github.com/users/dummygh"},
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        fasjson_client.search.return_value = SimpleNamespace(result=[{"username": "dummy"}])
        assert rule.matches(msg, tahrir_client) == set(["dummy"])
        fasjson_client.search.assert_called_once_with(
            github_username__exact="dummygh",
            page_size=40,
            page_number=1,
            _request_options={"headers": {"X-Fields": "username"}},
        )


def test_krb_awardee(fasproxy, tahrir_client, fm_config, user_exists):
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
            condition={"greater than or equal to": 1},
            previous=dict(
                filter=dict(categories=["pkgdb"]),
                operation="count",
            ),
            recipient="message.body['owner']",
            recipient_krb2fas="Yes",
        ),
        1,
        fm_config,
        fasproxy,
    )
    rule.setup(tahrir_client)

    # msg = Message(
    #     id="cedd7ab4-8a59-4704-bd1b-0e7297bf759c",
    #     topic="org.fedoraproject.prod.buildsys.build.state.change",
    #     headers={
    #         "sent-at": "2022-06-29T16:27:05+00:00",
    #     },
    #     body={
    #         "build_id": 1994993,
    #         "old": 0,
    #         "name": "dummy-test-package-gloster",
    #         "task_id": 88890394,
    #         "instance": "primary",
    #         "attribute": "state",
    #         "request": [
    #             "git+https://src.fedoraproject.org/rpms/dummy-test-package-gloster.git#aaf707bc5671ab5e00c5618d95bfd83803ca54c0",
    #             "rawhide",
    #             {},
    #         ],
    #         "owner": "packagerbot/os-master02.iad2.fedoraproject.org",
    #         "epoch": None,
    #         "version": "0",
    #         "release": "9242.fc37",
    #         "new": 1,
    #     },
    # )
    msg = Message(
        topic="org.fedoraproject.prod.buildsys.build.state.change",
        body={"owner": "packagerbot/os-master02.iad2.fedoraproject.org"},
    )

    with patch("fedbadges.rules.BadgeRule._get_current_value") as get_current_value:
        get_current_value.return_value = 1
        assert rule.matches(msg, tahrir_client) == set(["packagerbot"])
