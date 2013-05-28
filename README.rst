Fedora Badges
=============

This repo contains the consumer and the command nessicary to hook the fedora
badges stack (Tahrir, Tahrir-API, Tahrir-REST) into fedmsg.

Architecture
------------

fedbadges runs as a ``Consumer`` plugin to the ``fedmsg-hub`` (really,
a moksha-hub).  When started, it will load some initial configuration
(more on that later) and then sit quietly listening to the fedmsg bus.


* When a new message comes long, it looks to see if it matches one of
  any ``triggers`` it has registered.  If it does, it processes all of
  those triggers one after another.

* Each trigger must also define a ``criteria``, criteria may be more
  complicated, but they typically describe a set of queries to be
  made against the `datanommer
  <https://github.com/fedora-infra/datanommer>`_ database.

* For each of those criteria that do match, a badge is awarded to the
  respective user via the `tahrir_api
  <https://github.com/fedora-infra/tahrir-api>`_.  This amounts to
  adding a row in a database table.

Each rule (composed of some metadata, a trigger, and a set of criteria)
is defined on disk as a yaml file.  An early example of what we're
thinking for this can be found here:  https://gist.github.com/ralphbean/5443891

TODO - make a diagram describing how these pieces work together.
