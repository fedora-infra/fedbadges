from twisted.internet import defer, reactor


def _wait(_r):
    d = defer.Deferred()
    reactor.callLater(1, d.callback, None)
    return d


def test_load_badges_number(consumer):
    """Determine that we can load badges from file."""

    def _check(_r):
        assert len(consumer.badge_rules) == 5

    consumer._ready.addCallback(_wait).addCallback(_check)
    return consumer._ready


def test_load_badges_contents(consumer):
    """Determine that we can load badges from file."""

    def _check(_r):
        names = set([badge["name"] for badge in consumer.badge_rules])
        assert names == {
            "Like a Rock",
            "The Zen of Foo Bar Baz",
            "Junior Tagger (Tagger I)",
            "Speak Up!",
            "Long Life to Pagure (Pagure I)",
        }

    consumer._ready.addCallback(_wait).addCallback(_check)
    return consumer._ready
