import logging
from collections import defaultdict

import click
import fasjson_client
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)


def get_awards(fasjson, group_badges):
    awards = defaultdict(list)
    for group_badge in group_badges:
        group_name = group_badge["group"]
        badge_id = group_badge["badge"]
        membership_types = group_badge.get("memberships", ("members", "sponsors"))
        log.debug("Processing %s", group_name)
        for membership_type in membership_types:
            method = getattr(fasjson, f"list_group_{membership_type}")
            try:
                members = method(groupname=group_name).result
            except fasjson_client.errors.APIError:
                continue
            for user in members:
                username = user["username"]
                awards[badge_id].append(username)

    return awards


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
    fasjson = fasjson_client.Client(config["fasjson_base_url"])

    group_badges = config["group_badges"]

    # First, some validation that the badge ids actually exist.
    for badge_id in [gb["badge"] for gb in group_badges]:
        badge = tahrir.get_badge(badge_id=badge_id)
        if not badge:
            raise click.ClickException(f"{badge_id!r} is not a valid badge id")

    # Then, do a long query against FAS for our candidates.
    awards = get_awards(fasjson, group_badges)

    for badge_id, usernames in awards.items():
        badge = tahrir.get_badge(badge_id=badge_id)
        for username in usernames:
            award_badge(tahrir, badge, username)
