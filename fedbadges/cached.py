import logging

import pymemcache
from dogpile.cache import make_region
from dogpile.cache.proxy import ProxyBackend

log = logging.getLogger(__name__)
cache = make_region()


def configure(**kwargs):
    if not cache.is_configured:
        kwargs["wrap"] = [ErrorLoggingProxy]
        cache.configure(**kwargs)


class ErrorLoggingProxy(ProxyBackend):
    def set(self, key, value):
        try:
            self.proxied.set(key, value)
        except pymemcache.exceptions.MemcacheServerError:
            length = len(value)
            if length == 2:
                length = len(value[1])
            log.exception("Could not set the value in the cache (len=%s)", length)
