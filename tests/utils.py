""" Utilities for tests """


class MockHub(object):
    config = {
        "fedmsg.consumers.badges.enabled": True,
        "badges.yaml.directory": "tests/test_badges",
        "badges_global": {
            "database_uri": "sqlite:////tmp/sqlite.db",
            "badge_issuer": dict(
                issuer_id='Fedora Project',
                issuer_origin='http://badges.fedoraproject.com',
                issuer_name='Fedora Project',
                issuer_org='http://fedoraproject.org',
                issuer_contact='rdelinge@redhat.com'
            ),
        },
        "datanommer.sqlalchemy.url": "sqlite://",
        "validate_signatures":"False"
    }

    def subscribe(self, topic, callback):
        pass
