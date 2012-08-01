# -*- coding; utf-8 -*-
# Author: Ross Delinger
# Description: A system to award Fedora Badges (open badges)
# based on messages on the bu

from fedmsg.commands import command

extra_args = []

@command(name='fedmsg-badges', extra_args=extra_args, daemonizable=True)
def badges(**kw):
    """ Relay connections to the bus, and enabled the badges consumer """
    moksha_options = dict(
        zmq_subscribe_endpoints=','.join(
            ','.join(bunch) for bunch in kw['endpoints'].values()
        ),
    )
    kw.update(moksha_options)
    kw['fedmsg.consumers.badges.examplebadge.enabled'] = True

    from moksha.hub import main
    main(options=kw)
