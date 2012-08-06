config = dict(
    # Options for the fedmsg-fedbadges services
    badges_global = dict(
        database_uri='mysql://fedbadges:password@localhost/fedbadges',
            badge_issuer=dict(
                issuer_id='Fedora Project',
                issuer_origin='http://badges.fedoraproject.com',
                issuer_name='Fedora Project',
                issuer_org='http://fedoraproject.org',
                issuer_contact='rdelinge@redhat.com'
                )
    ),
)
