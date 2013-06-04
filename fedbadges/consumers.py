# -*- coding; utf-8 -*-
""" Consumers for producing openbadges by listening for messages on fedmsg

Authors:  Ross Delinger
          Ralph Bean
"""

import os.path
import yaml

import fedbadges.models
from paste.deploy.converters import asbool
from fedmsg.consumers import FedmsgConsumer
from tahrir_api.dbapi import TahrirDatabase

import logging
log = logging.getLogger("moksha.hub")


class FedoraBadgesConsumer(FedmsgConsumer):
    topic = "org.fedoraproject.*"
    config_key = "fedmsg.consumers.badges.enabled"

    def __init__(self, hub):
        self.badges = []
        self.hub = hub
        self.DBSession = None

        super(FedoraBadgesConsumer, self).__init__(hub)

        global_settings = hub.config.get("badges_global", {})

        database_uri = global_settings.get('database_uri')
        if not database_uri:
            raise ValueError('Badges consumer requires a database uri')

        self.tahrir = TahrirDatabase(database_uri)
        self.DBSession = self.tahrir.session_maker
        issuer = global_settings.get('badge_issuer')

        self.issuer_id = self.tahrir.add_issuer(
            issuer.get('issuer_origin'),
            issuer.get('issuer_name'),
            issuer.get('issuer_org'),
            issuer.get('issuer_contact')
        )

        directory = hub.config.get("badges.yaml.directory", "badges_yaml_dir")
        self.badges = self._load_badges_from_yaml(directory)

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
                    badge_rule = fedbadges.models.BadgeRule(badge, self.tahrir)
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

    def award_badge(self, email, badge_id, issued_on=None):
        """ A high level way to issue a badge to a Person.

        It adds the person if they don't exist, and creates an assertion for
        them.

        :type email: str
        :param email: This person's email addr

        :type badge_id: str
        :param badge_id: the id of the badge being awarded

        :type issued_on: DateTime
        :param issued_on: A datetime object with the time this badge was issued
        """

        self.tahrir.add_person(email)
        self.tahrir.add_assertion(badge_id, email, issued_on)

    def consume(self, msg):
        raise NotImplementError("I haven't written this yet")
        self.award_badge(email, badge_id)
