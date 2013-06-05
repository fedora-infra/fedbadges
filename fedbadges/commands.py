# -*- coding; utf-8 -*-
# Author: Ross Delinger
# Description: A system to award Fedora Badges (open badges)
# based on messages on the bu

from fedmsg.commands import BaseCommand
from fedbadges.consumers import FedoraBadgesConsumer


class BadgesCommand(BaseCommand):
    """ Relay connections to the bus, and enabled the badges consumer """
    name = 'fedmsg-badges'
    extra_args = []
    daemonizable = True

    def run(self):
        moksha_options = dict(
            zmq_subscribe_endpoints=','.join(
                ','.join(bunch) for bunch in self.config['endpoints'].values()
            ),
        )
        self.config.update(moksha_options)
        self.config['fedmsg.consumers.badges.enabled'] = True

        from moksha.hub import main
        main(
            options=self.config,
            # If you omit this argument, it will pick up *all* consumers.
            consumers=[FedoraBadgesConsumer],
            producers=[],
        )


def badges():
    command = BadgesCommand()
    command.execute()
