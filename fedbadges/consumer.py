"""Consumers for producing openbadges by listening for messages on fedmsg

Authors:  Ross Delinger
          Ralph Bean
          Aurelien Bompard
"""

import asyncio
import datetime
import logging
import time
from functools import partial

import datanommer.models
import tahrir_api.dbapi
from fedora_messaging.api import Message
from fedora_messaging.config import conf as fm_config
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .aio import Periodic
from .cached import configure as configure_cache
from .fas import FASProxy
from .rulesrepo import RulesRepo
from .utils import datanommer_has_message, notification_callback


log = logging.getLogger(__name__)

DEFAULT_RULES_RELOAD_INTERVAL = 15  # in minutes
MAX_WAIT_DATANOMMER = 5  # seconds


class FedoraBadgesConsumer:

    def __init__(self):
        self.config = fm_config["consumer_config"]
        self.badge_rules = []
        self.loop = asyncio.get_event_loop()
        self._ready = self.loop.create_task(self.setup())
        if not self.loop.is_running():
            self.loop.run_until_complete(self._ready)

    async def setup(self):
        # Five things need doing at start up time
        # 0) Set up a request local to hang thread-safe db sessions on.
        # 1) Initialize our connection to the Tahrir DB
        # 2) Initialize our connection to the datanommer DB.
        # 3) Load our badge definitions and rules from YAML.
        # Cache
        await self.loop.run_in_executor(None, self._initialize_cache)

        # Tahrir stuff.
        await self.loop.run_in_executor(None, self._initialize_tahrir_connection)

        # Datanommer stuff
        await self.loop.run_in_executor(None, self._initialize_datanommer_connection)

        # FASJSON stuff
        self.fasjson = await self.loop.run_in_executor(
            None, FASProxy, self.config["fasjson_base_url"]
        )

        # Load badge definitions
        self._rules_repo = RulesRepo(self.config, self.issuer_id, self.fasjson)
        self._rules_repo.setup()

        rules_reload_inteval = self.config.get(
            "rules_reload_interval", DEFAULT_RULES_RELOAD_INTERVAL
        )
        self._refresh_badges_task = Periodic(
            partial(self.loop.run_in_executor, None, self._reload_rules), rules_reload_inteval * 60
        )
        await self._refresh_badges_task.start(run_now=True)

    def _initialize_cache(self):
        cache_args = self.config.get("cache")
        configure_cache(**cache_args)

    def _initialize_tahrir_connection(self):
        if "email_domain" not in self.config:
            raise ValueError("Missing configuration key: 'email_domain'")

        database_uri = self.config.get("database_uri")
        if not database_uri:
            raise ValueError("Badges consumer requires a database uri")

        issuer = self.config["badge_issuer"]
        self.tahrir = tahrir_api.dbapi.TahrirDatabase(
            dburi=database_uri,
            autocommit=False,
            notification_callback=notification_callback,
        )
        self.issuer_id = self.tahrir.add_issuer(
            issuer.get("issuer_origin"),
            issuer.get("issuer_name"),
            issuer.get("issuer_url"),
            issuer.get("issuer_email"),
        )
        self.tahrir.session.commit()

    def _get_tahrir_client(self, session=None):
        return self.tahrir

    def _initialize_datanommer_connection(self):
        datanommer.models.init(self.config["datanommer_db_uri"])

    def award_badge(self, username, badge_rule, link=None):
        email = f"{username}@{self.config['email_domain']}"
        client = self._get_tahrir_client(self.tahrir.session)
        client.add_person(email)
        self.tahrir.session.commit()
        try:
            client.add_assertion(badge_rule.badge_id, email, None, link)
        except IntegrityError:
            # The badge has already been awarded by another consumer
            log.debug("Badge %s is already awarded to %s", badge_rule.badge_id, email)
            self.tahrir.session.rollback()
        else:
            self.tahrir.session.commit()

    def __call__(self, message: Message):
        try:
            self._process_message(message)
        except SQLAlchemyError:
            log.exception("Could not process message %s on %s", message.id, message.topic)
            # If we don't rollback, following queryies will fail: https://sqlalche.me/e/20/8s2b
            self.tahrir.session.rollback()
        # Always rollback the datanommer transaction after processing, it's read-only.
        datanommer.models.session.rollback()

    def _process_message(self, message: Message):
        self._wait_for_datanommer(message)
        tahrir = self._get_tahrir_client()

        # Update the leaderboard if necessary
        if message.topic.endswith("badges.badge.award"):
            person = tahrir.get_person(nickname=message.body["user"]["username"])
            log.debug("Computing the leaderboard for %s", person.nickname)
            tahrir.adjust_ranks(person)

        # Award every badge as appropriate.
        log.debug("Processing rules for %s on %s", message.id, message.topic)
        datagrepper_url = self.config["datagrepper_url"]
        link = f"{datagrepper_url}/v2/id?id={message.id}&is_raw=true&size=extra-large"
        for badge_rule in self.badge_rules:
            try:
                for recipient in badge_rule.matches(message, tahrir):
                    log.debug(
                        "Awarding %s to %s (message %s on %s)",
                        badge_rule.badge_id,
                        recipient,
                        message.id,
                        message.topic,
                    )
                    self.award_badge(recipient, badge_rule, link)
            except Exception:
                log.exception("Rule: %s, message: %s", repr(badge_rule), repr(message))
                self.tahrir.session.rollback()

        log.debug("Done with %s, %s", message.topic, message.id)

    def _reload_rules(self):
        log.debug("Check for badges updates in the repo")
        tahrir = self._get_tahrir_client()
        self.badge_rules = self._rules_repo.load_all(tahrir)

    def _wait_for_datanommer(self, message: Message):
        # If the message is recent, we ask datanommer if it already has it.
        # If it's older, we assume datanommer already has it and spare it a query.
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        a_minute_ago = now - datetime.timedelta(minutes=1)
        try:
            sent_at = message._headers["sent-at"]
            if sent_at.endswith("Z"):
                # Python 3.10 compatibility
                sent_at = sent_at[:-1] + "+00:00"
            sent_at = datetime.datetime.fromisoformat(sent_at)
        except (KeyError, TypeError, ValueError) as e:
            log.debug("Could not read the sent-at value: %s: %s", e.__class__.__name__, e)
            sent_at = None
        if sent_at is not None and sent_at < a_minute_ago:
            return  # It's kinda old, datanommer surely has it already

        yesterday = now - datetime.timedelta(days=1)
        for _i in range(MAX_WAIT_DATANOMMER * 2):
            if datanommer_has_message(message.id, since=yesterday):
                break
            log.debug("Waiting for the message to land in datanommer")
            time.sleep(0.5)
