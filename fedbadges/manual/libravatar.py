import hashlib
import logging

import click
import requests
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase
from tahrir_api.model import Person

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)

HTTP_TIMEOUT = 5


@click.command()
@option_debug
def main():
    setup_logging()
    config = fm_config["consumer_config"]
    uri = config["database_uri"]
    tahrir = TahrirDatabase(
        uri,
        notification_callback=fedbadges.utils.notification_callback,
    )
    badge = tahrir.get_badge("mugshot")

    persons = tahrir.session.query(Person).filter(Person.opt_out is False).all()
    already_has_it = [assertion.person for assertion in badge.assertions]

    good, bad = [], []
    for person in persons:

        if person in already_has_it:
            good.append(person)
            log.debug("Skipping %s", person)
            continue

        openid = f"http://{person.nickname}.id.fedoraproject.org/"
        hash = hashlib.sha256(openid.encode("utf-8")).hexdigest()
        url = f"https://seccdn.libravatar.org/avatar/{hash}?d=404"

        response = None
        for i in range(10):
            log.debug("Try %s on %s", i, url)
            try:
                response = requests.get(url, timeout=HTTP_TIMEOUT)
                break
            except requests.exceptions.SSLError as e:
                print(" * failed, trying again", str(e))

        if response is None:
            raise

        if response.status_code == 200:
            log.info("%s totally gets the mugshot badge.", person.nickname)
            good.append(person)
            award_badge(tahrir, badge.id, person.email, check_existing=False)
        else:
            bad.append(person)

    log.info("%s good peoples", len(good))
    log.info("%s bad peoples", len(bad))


if __name__ == "__main__":
    main()
