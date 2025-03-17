"""Utilities for tests"""

import datetime

from bodhi.messages.schemas.update import UpdateRequestTestingV1


def get_rule(rules, name):
    for rule in rules:
        if rule["name"] == name:
            return rule


class MockedDatanommerMessage:
    def __init__(self, message):
        self.msg_id = message.id
        self.topic = message.topic
        self.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        self.msg = message.body
        self.headers = message._properties.headers
        self.users = message.usernames
        self.packages = message.packages


example_real_bodhi_message = UpdateRequestTestingV1(
    topic="org.fedoraproject.prod.bodhi.update.request.testing",
    body={
        "agent": "lmacken",
        "update": {
            "alias": "FEDORA-2019-f1ca3c00e5",
            "status": "pending",
            "critpath": False,
            "stable_karma": 3,
            "date_pushed": None,
            "title": "gnome-settings-daemon-3.6.1-1.fc18,control-center-3.6.1-1.fc18",
            "nagged": None,
            "comments": [
                {
                    "group": None,
                    "author": "bodhi",
                    "text": "This update has been submitted for testing by hadess. ",
                    "karma": 0,
                    "anonymous": False,
                    "timestamp": 1349718539.0,
                    "update_title": "gnome-settings-daemon-3.6.1-1.fc18,"
                    + "control-center-3.6.1-1.fc18",
                }
            ],
            "updateid": None,
            "type": "bugfix",
            "close_bugs": True,
            "date_submitted": 1349718534.0,
            "unstable_karma": -3,
            "release": {
                "dist_tag": "f18",
                "locked": True,
                "long_name": "Fedora 18",
                "name": "F18",
                "id_prefix": "FEDORA",
            },
            "approved": None,
            "builds": [
                {
                    "nvr": "gnome-settings-daemon-3.6.1-1.fc18",
                    "package": {
                        "suggest_reboot": False,
                        "committers": ["hadess", "ofourdan", "mkasik", "cosimoc"],
                        "name": "gnome-settings-daemon",
                    },
                },
                {
                    "nvr": "control-center-3.6.1-1.fc18",
                    "package": {
                        "suggest_reboot": False,
                        "committers": [
                            "ctrl-center-team",
                            "ofourdan",
                            "ssp",
                            "ajax",
                            "alexl",
                            "jrb",
                            "mbarnes",
                            "caolanm",
                            "davidz",
                            "mclasen",
                            "rhughes",
                            "hadess",
                            "johnp",
                            "caillon",
                            "whot",
                            "rstrode",
                        ],
                        "name": "control-center",
                    },
                },
            ],
            "date_modified": None,
            "notes": "This update fixes numerous bugs in the new Input "
            + "Sources support, the Network panel and adds a help "
            + "screen accessible via Wacom tablets's buttons.",
            "request": "testing",
            "bugs": [],
            "critpath_approved": False,
            "karma": 0,
            "submitter": "hadess",
            "user": {"name": "hadess"},
        },
    },
)
