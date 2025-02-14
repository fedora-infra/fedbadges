import datetime
import logging

import click
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils
from fedbadges.fas import FASProxy

from .utils import award_badge, option_debug, setup_logging


# Users in the fedora-contributor group are members of at least 1 group.
REQUIRED_GROUPS = ["fedora-contributor"]

log = logging.getLogger(__name__)


@click.command()
@option_debug
def main(debug):
    setup_logging(debug=debug)
    config = fm_config["consumer_config"]
    uri = config["database_uri"]
    tahrir = TahrirDatabase(
        uri,
        notification_callback=fedbadges.utils.notification_callback,
    )
    badge = tahrir.get_badge(badge_id="badge-off!")
    if not badge:
        raise ValueError("badge does not exist")

    fasjson = FASProxy(config["fasjson_base_url"])

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    year = datetime.timedelta(days=365.5)
    mapping = {
        "egg": year * 1,
        "embryo": year * 2,
        "tadpole": year * 3,
        "tadpole-with-legs": year * 5,
        "froglet": year * 7,
        "adult-frog": year * 10,
    }

    # Query IPA for users created before the threshold
    for badge_id, delta in list(mapping.items()):
        badge = tahrir.get_badge(badge_id=badge_id)
        if not badge.id:
            log.error("Badge %s does not exist", badge_id)
            continue
        threshold = now - delta
        for person in fasjson.search_user(
            group=REQUIRED_GROUPS, creation__before=threshold, _fields=["username"]
        ):
            email = f"{person['username']}@{config['email_domain']}"
            award_badge(tahrir, badge, email)


if __name__ == "__main__":
    main()
