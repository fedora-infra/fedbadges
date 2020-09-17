""" Utilities for tests """


class MockHub(object):
    config = {
        "fedmsg.consumers.badges.enabled": True,
        "badges.yaml.directory": "tests/test_badges",
        "badges_global": {
            "badge_issuer": dict(
                issuer_entity_id="dkcsldkmlkc92jn",
                issuer_name="Fedora Project",
                issuer_origin="http://badges.fedoraproject.com",
                issuer_url="http://fedoraproject.org",
                issuer_email="badges@fedoraproject.org",
            ),
            "badgr_user": dict(
                username="test_user",
                password="password",
                client_id="public",
                base_url="http://localhost:8000",
            ),
        },
        "datanommer.sqlalchemy.url": "sqlite://",
        "validate_signatures": "False",
    }

    def subscribe(self, topic, callback):
        pass
