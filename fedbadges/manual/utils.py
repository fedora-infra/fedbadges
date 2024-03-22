import logging

import click


_log = logging.getLogger(__name__)

option_debug = click.option("--debug", is_flag=True, default=False, help="enable debugg logging")


def setup_logging(debug=False):
    log_format = "[%(asctime)s][%(levelname)s] %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG if debug else logging.INFO)


def award_badge(tahrir, badge, email, check_existing=True):
    if check_existing and tahrir.assertion_exists(badge.id, email):
        _log.debug("%s already has %s, skipping", email, badge.id)
        return

    # time.sleep(1)
    _log.info("Awarding %s to %s", badge.id, email)
    try:
        tahrir.add_assertion(badge.id, email, None)
    except Exception:
        tahrir.session.rollback()
        _log.exception("Failure awarding badge %s to %s", badge.id, email)
