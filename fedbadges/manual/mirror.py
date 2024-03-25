import logging

import click
import requests
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)

HTTP_TIMEOUT = 5


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

    url = "https://admin.fedoraproject.org/mirrormanager/api/mirroradmins"
    response = requests.get(url, timeout=HTTP_TIMEOUT)

    if not response.ok:
        raise click.ClickException("Couldn't read the mirrormanager/mirroradmins list.")

    usernames = response.json()["admins"]

    badge = tahrir.get_badge(badge_id="mirror,-mirror-on-the-wall")
    if not badge:
        raise ValueError("Badge does not exist")

    for username in usernames:
        email = f"{username}@fedoraproject.org"

        person = tahrir.get_person(person_email=email)
        if not person:
            log.info("%s does not exist.  Creating.", email)
            tahrir.add_person(email, nickname=username)

        award_badge(tahrir, badge, email)


if __name__ == "__main__":
    main()
