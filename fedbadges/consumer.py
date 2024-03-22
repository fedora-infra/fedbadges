""" Consumers for producing openbadges by listening for messages on fedmsg

Authors:  Ross Delinger
          Ralph Bean
          Aurelien Bompard
"""

import asyncio
import logging
import os.path
import threading
import time

import datanommer.models
import fasjson_client
import tahrir_api.dbapi
import yaml
from fedora_messaging.api import Message
from fedora_messaging.config import conf as fm_config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import fedbadges.rules


log = logging.getLogger(__name__)

DEFAULT_CONSUME_DELAY = 3
DEFAULT_DELAY_LIMIT = 100


class FedoraBadgesConsumer:
    delay_limit = 100

    def __init__(self):
        self.config = fm_config["consumer_config"]
        self.consume_delay = int(self.config.get("consume_delay", DEFAULT_CONSUME_DELAY))
        self.delay_limit = int(self.config.get("delay_limit", DEFAULT_DELAY_LIMIT))
        self.badge_rules = []
        self.lock = threading.Lock()
        # Thread-local stuff
        self.l = threading.local()

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

        # Tahrir stuff.
        self._initialize_tahrir_connection()

        # Datanommer stuff
        self._initialize_datanommer_connection()

        # FASJSON stuff
        self.fasjson = fasjson_client.Client(self.config["fasjson_base_url"])

        # Load badge definitions
        directory = self.config["badges_directory"]
        self.badge_rules = self._load_badges_from_yaml(directory)

    def _initialize_tahrir_connection(self):
        database_uri = self.config.get("database_uri")
        if not database_uri:
            raise ValueError("Badges consumer requires a database uri")
        self.TahrirDbSession = scoped_session(
            sessionmaker(
                bind=create_engine(database_uri),
            )
        )
        issuer = self.config["badge_issuer"]

        with self.TahrirDbSession() as session:
            client = self._get_tahrir_client(session=session)
            self.issuer_id = client.add_issuer(
                issuer.get("issuer_origin"),
                issuer.get("issuer_name"),
                issuer.get("issuer_url"),
                issuer.get("issuer_email"),
            )
            session.commit()

    def _get_tahrir_client(self, session=None):
        if hasattr(self.l, "tahrir"):
            return self.l.tahrir

        session = session or self.TahrirDbSession()
        self.l.tahrir = tahrir_api.dbapi.TahrirDatabase(
            session=session,
            autocommit=False,
            notification_callback=fedbadges.utils.notification_callback,
        )
        session.commit()
        return self.l.tahrir

    def _initialize_datanommer_connection(self):
        datanommer.models.init(self.config["datanommer_db_uri"])

    def _load_badges_from_yaml(self, directory):
        # badges indexed by trigger
        badges = []
        directory = os.path.abspath(directory)
        log.info("Looking in %r to load badge definitions" % directory)
        client = self._get_tahrir_client()
        for root, _dirs, files in os.walk(directory):
            for partial_fname in files:
                fname = root + "/" + partial_fname
                badge = self._load_badge_from_yaml(fname)

                if not badge:
                    continue

                try:
                    badge_rule = fedbadges.rules.BadgeRule(
                        badge, client, self.issuer_id, self.config, self.fasjson
                    )
                    badge_rule.setup()
                    badges.append(badge_rule)
                except ValueError as e:
                    log.error("Initializing rule for %r failed with %r", fname, e)

        log.info("Loaded %i total badge definitions" % len(badges))
        return badges

    def _load_badge_from_yaml(self, fname):
        log.debug("Loading %r" % fname)
        try:
            with open(fname) as f:
                return yaml.safe_load(f.read())
        except Exception as e:
            log.error("Loading %r failed with %r", fname, e)
            return None

    def award_badge(self, username, badge_rule, link=None):
        email = f"{username}@fedoraproject.org"
        with self.TahrirDbSession() as session:
            client = self._get_tahrir_client(session)
            client.add_person(email)
            session.commit()
            client.add_assertion(badge_rule.badge_id, email, None, link)
            session.commit()

    def __call__(self, message: Message):
        # First thing, we receive the message, but we put ourselves to sleep to
        # wait for a moment.  The reason for this is that, when things are
        # 'calm' on the bus, we receive messages "too fast".  A message that
        # arrives to the badge awarder triggers (usually) a check against
        # datanommer to count messages.  But if we try to count them before
        # this message arrives at datanommer, we'll get skewed results!  Race
        # condition.  We go to sleep to allow ample time for datanommer to
        # consume this one before we go and start doing checks on it.
        # TODO: make a SQL query in datanommer instead of waiting
        # TODO: scratch that, check if the current message is in the matched messages
        #       when querying datanommer, and if it's not add 1 to the count.
        time.sleep(self.consume_delay)

        datagrepper_url = self.config["datagrepper_url"]
        link = f"{datagrepper_url}/id?id={message.id}&is_raw=true&size=extra-large"

        # Define this so we can refer to it in error handling below
        badge_rule = None

        # Award every badge as appropriate.
        log.debug("Received %s, %s", message.topic, message.id)
        for badge_rule in self.badge_rules:
            try:
                for recipient in badge_rule.matches(message):
                    self.award_badge(recipient, badge_rule, link)
            except Exception:
                log.exception("Rule: %s, message: %s", repr(badge_rule), repr(message))

        log.debug("Done with %s, %s", message.topic, message.id)
