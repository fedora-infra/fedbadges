# -*- coding; utf-8 -*-
""" Consumers for producing openbadges by listening for messages on fedmsg

Authors:  Ross Delinger
          Ralph Bean
"""

import os.path
import yaml
import traceback

import fedmsg
import fedmsg.consumers
import tahrir_api.dbapi
import datanommer.models

import fedbadges.rules

import logging
log = logging.getLogger("moksha.hub")


class FedoraBadgesConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = "org.fedoraproject.*"
    config_key = "fedmsg.consumers.badges.enabled"

    def __init__(self, hub):
        self.badge_rules = []
        self.hub = hub
        self.DBSession = None

        super(FedoraBadgesConsumer, self).__init__(hub)

        # Three things need doing at start up time
        # 1) Initialize our connection to the tahrir DB and perform some
        #    administrivia.
        # 2) Initialize our connection to the datanommer DB.
        # 3) Load our badge definitions and rules from YAML.

        # Tahrir stuff
        self._initialize_tahrir_connection()

        # Datanommer stuff
        self._initialize_datanommer_connection()

        # Load badge definitions
        directory = hub.config.get("badges.yaml.directory", "badges_yaml_dir")
        self.badge_rules = self._load_badges_from_yaml(directory)

    def _initialize_tahrir_connection(self):
        global_settings = self.hub.config.get("badges_global", {})

        database_uri = global_settings.get('database_uri')
        if not database_uri:
            raise ValueError('Badges consumer requires a database uri')

        self.tahrir = tahrir_api.dbapi.TahrirDatabase(database_uri)
        self.DBSession = self.tahrir.session_maker
        issuer = global_settings.get('badge_issuer')

        self.issuer_id = self.tahrir.add_issuer(
            issuer.get('issuer_origin'),
            issuer.get('issuer_name'),
            issuer.get('issuer_org'),
            issuer.get('issuer_contact')
        )

    def _initialize_datanommer_connection(self):
        datanommer.models.init(self.hub.config['datanommer.sqlalchemy.url'])

    def _load_badges_from_yaml(self, directory):
        # badges indexed by trigger
        badges = []
        directory = os.path.abspath(directory)
        log.info("Looking in %r to load badge definitions" % directory)
        for root, dirs, files in os.walk(directory):
            for partial_fname in files:
                fname = root + "/" + partial_fname
                badge = self._load_badge_from_yaml(fname)

                if not badge:
                    continue

                try:
                    badge_rule = fedbadges.rules.BadgeRule(badge, self.tahrir)
                    badges.append(badge_rule)
                except ValueError as e:
                    log.error("Initializing rule for %r failed with %r" % (
                        fname, e))

        log.info("Loaded %i total badge definitions" % len(badges))
        return badges

    def _load_badge_from_yaml(self, fname):
        log.debug("Loading %r" % fname)
        try:
            with open(fname, 'r') as f:
                return yaml.load(f.read())
        except Exception as e:
            log.error("Loading %r failed with %r" % (fname, e))
            return None

    def award_badge(self, username, badge_id):
        """ A high level way to issue a badge to a Person.

        It adds the person if they don't exist, and creates an assertion for
        them.

        :type username: str
        :param username: This person's username.

        :type badge_id: str
        :param badge_id: the id of the badge being awarded
        """

        log.info("Awarding badge %r to %r" % (badge_id, username))
        email = "%s@fedoraproject.org" % username

        self.tahrir.add_person(email)
        self.tahrir.add_assertion(badge_id, email, None)

        fedmsg.publish(topic="badge.award",
                       msg=dict(badge_id=badge_id, username=username))

    def consume(self, msg):

        # Strip the moksha envelope
        msg = msg['body']

        # Define this so we can refer to it in error handling below
        badge_rule = None

        # Award every badge as appropriate.
        try:
            log.info("Received %r." % msg['topic'])
            for badge_rule in self.badge_rules:
                for recipient in badge_rule.matches(msg):
                    self.award_badge(recipient, badge_rule.badge_id)
        except Exception as e:
            log.error("Failure in badge awarder! %r Details to follow:" % e)
            log.error("Considering badge: %r" % badge_rule)
            log.error("Received Message: %r" % msg)
            log.error(traceback.format_exc())
