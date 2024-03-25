import datetime
import logging
import os
import subprocess

import yaml

import fedbadges.rules


log = logging.getLogger(__name__)


class RulesRepo:

    def __init__(self, config, issuer_id, fasjson):
        self.config = config
        self.issuer_id = issuer_id
        self.fasjson = fasjson
        self.directory = os.path.abspath(self.config["badges_repo"])
        self._last_rules_load = None
        self.rules = []

    def setup(self):
        self._mark_safe()

    def _mark_safe(self):
        result = subprocess.run(
            ["/usr/bin/git", "config", "--get-all", "safe.directory"],  # noqa: S603
            text=True,
            stdout=subprocess.PIPE,
        )
        if result.returncode == 1:
            # Option isn't set
            safe_dirs = []
        else:
            result.check_returncode()
            safe_dirs = result.stdout.strip().split("\n")
        log.debug("Git safe dirs: %r", safe_dirs)
        if self.directory not in safe_dirs:
            log.debug("Adding %s to git's safe dirs", self.directory)
            subprocess.run(
                [  # noqa: S603
                    "/usr/bin/git",
                    "config",
                    "--global",
                    "--add",
                    "safe.directory",
                    self.directory,
                ],
                check=True,
            )

    def load_all(self, tahrir_client, force=False):
        if force or self._needs_update():
            self.rules = self._load_all(tahrir_client)
        return self.rules

    def _load_all(self, tahrir_client):
        self._last_rules_load = datetime.datetime.now()
        rules_dir = os.path.join(self.directory, "rules")
        # badges indexed by trigger
        badges = []
        log.info("Looking in %r to load badge definitions", rules_dir)
        for root, _dirs, files in os.walk(rules_dir):
            for partial_fname in files:
                fname = root + "/" + partial_fname
                badge = self._load_badge_from_yaml(fname)

                if not badge:
                    continue

                try:
                    badge_rule = fedbadges.rules.BadgeRule(
                        badge, self.issuer_id, self.config, self.fasjson
                    )
                    badge_rule.setup(tahrir_client)
                    badges.append(badge_rule)
                except ValueError as e:
                    log.error("Initializing rule for %r failed with %r", fname, e)

        log.info("Loaded %s total badge definitions", len(badges))
        return badges

    def _load_badge_from_yaml(self, fname):
        log.debug("Loading %r" % fname)
        try:
            with open(fname) as f:
                return yaml.safe_load(f.read())
        except Exception as e:
            log.error("Loading %r failed with %r", fname, e)
            return None

    def _needs_update(self):
        if self._last_rules_load is None:
            return True
        result = subprocess.run(
            [  # noqa: S603
                "/usr/bin/git",
                "-C",
                self.directory,
                "log",
                "-1",
                r"--pretty=format:%aI",
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        last_commit_time = datetime.datetime.fromisoformat(result.stdout.strip())
        return last_commit_time > self._last_rules_load
