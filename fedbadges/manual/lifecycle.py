import datetime
import logging
import re

import click
import ldap
import ldap.sasl
from fedora_messaging.config import conf as fm_config
from ldap.controls.libldap import SimplePagedResultsControl
from tahrir_api.dbapi import TahrirDatabase

import fedbadges.utils

from .utils import award_badge, option_debug, setup_logging


log = logging.getLogger(__name__)
LDAP_CONF = "/etc/ipa/ldap.conf"


class LDAPClient:

    def __init__(self):
        self.config = {}
        self.conn = None
        self._read_config()

    def _read_config(self):
        conf_re = re.compile(r"^([A-Z_]+)\s+(.+)$")
        with open(LDAP_CONF) as cf:
            for line in cf:
                mo = conf_re.match(line.strip())
                if mo is None:
                    continue
                variable = mo.group(1)
                value = mo.group(2)
                self.config[variable] = value

    def connect(self):
        self.conn = ldap.initialize(self.config["URI"].split(" ")[0])
        self.conn.protocol_version = 3
        self.conn.sasl_interactive_bind_s("", ldap.sasl.gssapi())

    def search(self, base, filters, attrs):
        page_size = 1000
        base_dn = "{base},{main_base}".format(base=base, main_base=self.config["BASE"])
        page_cookie = ""
        while True:
            page_control = SimplePagedResultsControl(
                criticality=False, size=page_size, cookie=page_cookie
            )
            msgid = self.conn.search_ext(
                base_dn,
                ldap.SCOPE_SUBTREE,
                filters,
                attrlist=attrs,
                serverctrls=[page_control],
            )
            rtype, rdata, rmsgid, serverctrls = self.conn.result3(msgid)
            for _dn, obj in rdata:
                yield obj
            for ctrl in serverctrls:
                if isinstance(ctrl, SimplePagedResultsControl):
                    page_cookie = ctrl.cookie
                    break
            if not page_cookie:
                break


def get_fas_userlist(threshold):
    # os.environ["KRB5_CLIENT_KTNAME"] = fm_config.get("keytab")
    ldap_client = LDAPClient()
    ldap_client.connect()
    filters = "(&(fasCreationTime<={})(objectclass=fasUser))".format(
        threshold.strftime("%Y%m%d%H%M%SZ")
    )
    response = ldap_client.search(
        base="cn=users,cn=accounts", filters=filters, attrs=["uid", "memberof"]
    )
    for res in response:
        groups = []
        for groupdn in res.get("memberof", []):
            groupdn = groupdn.decode("ascii")
            if not groupdn.endswith(",cn=groups,cn=accounts,{}".format(ldap_client.config["BASE"])):
                continue
            groupname = groupdn.split(",")[0].split("=")[1]
            if groupname == "ipausers":
                continue  # Assume all groups are FAS groups except this one
            groups.append(groupname)
        yield {"username": res["uid"][0].decode("ascii"), "groups": groups}


@click.command()
@option_debug
def main(debug):
    setup_logging(debug=debug)
    config = fm_config["consumer_config"]
    uri = config["database_uri"]
    tahrir = TahrirDatabase(
        uri,
        notification_callback=fedbadges.utils.notification_callback,
    )
    badge = tahrir.get_badge(badge_id="badge-off!")
    if not badge:
        raise ValueError("badge does not exist")

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    year = datetime.timedelta(days=365.5)
    mapping = {
        "egg": year * 1,
        "embryo": year * 2,
        "tadpole": year * 3,
        "tadpole-with-legs": year * 5,
        "froglet": year * 7,
        "adult-frog": year * 10,
    }

    # Query IPA for users created before the threshold
    for badge_id, delta in list(mapping.items()):
        badge = tahrir.get_badge(badge_id=badge_id)
        if not badge.id:
            log.error("Badge %s does not exist", badge_id)
            continue
        threshold = now - delta
        for person in get_fas_userlist(threshold):
            if len(person["groups"]) < 2:
                continue
            email = person["username"] + "@fedoraproject.org"
            award_badge(tahrir, badge, email)


if __name__ == "__main__":
    main()
