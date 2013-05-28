from badges import FedoraBadgesConsumer
import os.path

import logging
log = logging.getLogger("moksha.hub")


class YAMLConsumer(FedoraBadgesConsumer):
    topic = "org.fedoraproject.*"

    def __init__(self, hub):
        self.name = "yamlconsumer"

        super(YAMLConsumer, self).__init__(hub, self.name)

        directory = hub.config.get("badges.yaml.directory", "badges_yaml_dir")
        self._load_badges_from_yaml(directory)

    def _load_badges_from_yaml(self, directory):
        # badges indexed by trigger
        self.badges = []
        directory = os.path.abspath(directory)
        log.info("Looking in %r to load badge definitions" % directory)
        for root, dirs, files in os.walk(directory):
            for partial_fname in files:
                fname = root + "/" + partial_fname
                self.badges.append(self._load_badge_from_yaml(fname))

        log.info("Loaded %i total badge definitions" % len(self.badges))

    def _load_badge_from_yaml(self, fname):
        log.debug("Loading %r" % fname)
        try:
            with open(fname, 'r') as f:
                return yaml.loads(f.read())
        except Exception as e:
            log.error("Loading %r failed with %r" % (fname, e))

    def consume(self, msg):
        raise NotImplementError("I haven't written this yet")
        self.award_badge(email, badge_id)
