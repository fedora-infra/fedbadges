Fedora Badges
=============

This repo contains the consumer and the command nessicary to hook the fedora
badges stack (Tahrir, Tahrir-API, Tahrir-REST) into fedmsg.

Architecture
------------

fedbadges runs as a ``Consumer`` plugin to the ``fedmsg-hub`` (really,
a moksha-hub).  When started, it will load some initial configuration
and a set of ``BadgeRules`` (more on that later) and then sit quietly
listening to the fedmsg bus.  Each rule (composed of some metadata,
a ``trigger``, and a set of ``criteria``) is defined on disk as a yaml file.

* When a new message comes long, our ``Consumer`` looks to see if it matches
  any of the ``BadgeRules`` it has registered.

* Each BadgeRule must define a ``trigger`` -- a `lightweight` check.
  When processing a message, this is the first thing that is checked.  It
  defines a *pattern* that the message must match.  If the message does not
  match, then the current BadgeRule is discarded and processing moves to
  the next.

  In english, a ``trigger`` is typically something like "any bodhi message"
  or "messages only from the failure of a koji build".  More on their
  specification below.

* BadgeRules must also define a set of ``criteria`` -- more `heavyweight`
  checks.  During the processing of a newly received message, if the
  message matches a BadgeRule's ``trigger``, the ``criteria`` is then
  considered.  This typically involves a more expensive query to the
  `datanommer <https://github.com/fedora-infra/datanommer>`_ database.

  In english, a BadgeRule ``criteria`` may read something like "$user has
  pushed 200 bodhi updates to stable" or "$user chaired an IRC meeting".

  **Aside:** Although datanommer is the only currently supported backend, we
  can implement other queryable backend in the future as needed like FAS2
  (to see if the user is in X number of groups) or even off-site services
  like libravatar (to award a badge if the user is a user of the AGPL web
  service).

* If a badge's ``trigger`` and ``criteria`` both match, then the badge is
  awarded.  If the BadgeRule doesn't specify, we award the badge to all
  usernames returned by a call to ``fedmsg.meta.msg2usernames(msg)``.

  That is usually correct -- but sometimes, a BadgeRule needs to specify
  that one particular user (not all related users) should be recipients of
  the badge.  In this case, the BadgeRule may define a ``recipient_key``
  in dot-notation that instructs the ``Consumer`` how to extract the
  recipient's username from the received message.

  The badge is awarded to our deserving user via the `tahrir_api
  <https://github.com/fedora-infra/tahrir-api>`_.  At the end of the day,
  this amounts to adding a row in a database table for the `Tahrir
  <https://github.com/fedora-infra/tahrir>`_ application.

Configuration - Global
----------------------

fedbadges needs three major pieces of global configuration.
All configuration is loaded in the standard fedmsg way, from
python files in ``/etc/fedmsg.d/``.

First, generic and tahrir-related configuration.  See
`fedmsg.d/badges-global.py
<https://github.com/fedora-infra/fedbadges/blob/develop/fedmsg.d/badges-global.py>`_
in the git repo for an example.

Second, datanommer connection information.  See
`fedmsg.d/datanommer.py
<https://github.com/fedora-infra/fedbadges/blob/develop/fedmsg.d/datanommer.py>`_
in the git repo for an example.

Third, fedbadges emits its own fedmsg messages when it awards badges.  It will
need its own endpoint definitions for this.  See `fedmsg.d/endpoints.py
<https://github.com/fedora-infra/fedbadges/blob/develop/fedmsg.d/endpoints.py>`_
in the git repo for an example.
