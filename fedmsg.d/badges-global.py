config = {
    # Options for the fedmsg-fedbadges services
    "fedmsg.consumers.badges.enabled": True,
    "badges.yaml.directory": "tests/test_badges",
    "badges_global": {
        "database_uri": "sqlite:////tmp/test-badges-sqlite.db",
        "badge_issuer": dict(
            issuer_id='Fedora Project',
            issuer_origin='http://badges.fedoraproject.com',
            issuer_name='Fedora Project',
            issuer_org='http://fedoraproject.org',
            issuer_contact='badges@fedoraproject.org',
        ),
    },
}
