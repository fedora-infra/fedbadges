config = {
    # We need to tell the fedmsg-hub that it should load our consumer on start.
    "fedmsg.consumers.badges.enabled": True,

    # This tells the consumer where to look for its BadgeRule definitions.  It
    # may be a relative or an absolute path on the file system.
    "badges.yaml.directory": "tests/test_badges",

    # Number of seconds to delay before consuming a message for our event loop.
    # This is here to help us mitigate distributed race conditions between
    # fedbadges and datanommer.
    "badges.consume_delay": 1,

    # This is a dictionary of tahrir-related configuration
    "badges_global": {

        # This is a sqlalchemy URI that points to the tahrir DB.  In
        # production, this will be a postgres URI.
        "database_uri": "sqlite:////tmp/test-badges-sqlite.db",

        # This is a set of data that tells our consumer what Open Badges Issuer
        # should be kept as the issuer of all the badges we create.
        "badge_issuer": dict(
            issuer_id='Fedora Project',
            issuer_origin='http://badges.fedoraproject.com',
            issuer_name='Fedora Project',
            issuer_org='http://fedoraproject.org',
            issuer_contact='badges@fedoraproject.org',
        ),
    },

    "fedbadges.datagrepper_url": "https://apps.fedoraproject.org/datagrepper",
}
