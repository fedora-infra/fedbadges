import hashlib
import logging
import sys
import traceback

import backoff
import click
import requests
from fedora_messaging.config import conf as fm_config
from requests_ratelimiter import LimiterSession
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging

log = logging.getLogger(__name__)

HTTP_TIMEOUT = 5
HTTP_RATE_LIMIT = {"per_second": 1}


def _backoff_hdlr(details):
    log.warning("Request to Libravatar failed, retrying.")


def _giveup_hdlr(details):
    log.warning(
        f"Request to Libravatar failed, giving up. {traceback.format_tb(sys.exc_info()[2])}"
    )


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
    max_tries=3,
    on_backoff=_backoff_hdlr,
    on_giveup=_giveup_hdlr,
    raise_on_giveup=False,
)
def query_libravatar(http, email):
    hash = hashlib.sha256(email.encode("utf-8")).hexdigest()
    url = f"https://seccdn.libravatar.org/avatar/{hash}?d=404"
    log.debug("Looking for an avatar of %s at %s", email, url)
    return http.get(url, timeout=HTTP_TIMEOUT)


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
    badge = tahrir.get_badge(badge_id="mugshot")
    http = LimiterSession(**HTTP_RATE_LIMIT)

    persons = tahrir.get_all_persons()
    already_has_it = [assertion.person for assertion in badge.assertions]

    good, bad = [], []
    for person in persons:

        if person in already_has_it:
            good.append(person)
            log.debug("Skipping %s", person)
            continue

        response = query_libravatar(http, person.avatar)
        if response is None:
            # Query failed, ignore
            continue

        if response.ok:
            log.info("%s totally gets the mugshot badge.", person.nickname)
            good.append(person)
            award_badge(tahrir, badge, person.email, check_existing=False)
        else:
            bad.append(person)

    log.info("%s good peoples", len(good))
    log.info("%s bad peoples", len(bad))


if __name__ == "__main__":
    main()
