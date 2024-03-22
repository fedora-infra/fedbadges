import logging
import subprocess
import tempfile

import click
import fasjson_client
from fedora_messaging.config import conf as fm_config
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)


badge = None
http_client = None


def gather_authors(repodir):
    result = subprocess.run(
        ["/usr/bin/git", "log", r"--pretty=tformat:%ae"],  # noqa: S603
        cwd=repodir,
        text=True,
        stdout=subprocess.PIPE,
    )
    yield from set(result.stdout.splitlines())


def email_to_fas_accounts(fasjson, email):
    response = fasjson.search(email__exact=email)
    if response.page["total_results"] != 1:
        return None
    return response.result[0]["username"]


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
    badge = tahrir.get_badge(badge_id="badge-off!")
    if not badge:
        raise ValueError("badge does not exist")
    fasjson = fasjson_client.Client(config["fasjson_base_url"])
    repos = ["tahrir", "tahrir-api", "fedbadges"]
    for repo in repos:
        with tempfile.TemporaryDirectory() as tmpdir:
            log.info("Trying %s", repo)
            subprocess.run(
                [  # noqa: S603
                    "/usr/bin/git",
                    "clone",
                    f"https://github.com/fedora-infra/{repo}.git",
                    tmpdir,
                ]
            )
            for email in gather_authors(tmpdir):
                log.debug("Considering email %s", email)
                username = email_to_fas_accounts(fasjson, email)
                log.debug("Considering user %s", username)
                award_badge(tahrir, badge, username)


if __name__ == "__main__":
    main()
