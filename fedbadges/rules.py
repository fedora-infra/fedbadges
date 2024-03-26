""" Models for fedbadges.

The primary thing here is a "BadgeRule" which is an in-memory working
abstraction of the trigger and criteria required to award a badge.

Authors:    Ralph Bean
"""

import abc
import copy
import functools
import inspect
import logging
import re

import datanommer.models
from fedora_messaging.api import Message
from tahrir_api.dbapi import TahrirDatabase

from fedbadges.utils import (
    # These are all in-process utilities
    construct_substitutions,
    email2fas,
    format_args,
    get_pagure_authors,
    graceful,
    nick2fas,
    recursive_lambda_factory,
    single_argument_lambda_factory,
    # These make networked API calls
    user_exists_in_fas,
)


log = logging.getLogger(__name__)


# Match OpenID agent strings, i.e. http://FAS.id.fedoraproject.org
def openid2fas(openid, config):
    id_provider_hostname = re.escape(config["id_provider_hostname"])
    m = re.search(f"^https?://([a-z][a-z0-9]+)\\.{id_provider_hostname}$", openid)
    if m:
        return m.group(1)
    return openid


def github2fas(uri, config, fasjson):
    m = re.search(r"^https?://api.github.com/users/([a-z][a-z0-9-]+)$", uri)
    if not m:
        return uri
    github_username = m.group(1)
    response = fasjson.search_users(github_username__exact=github_username)
    if not response.ok:
        return None
    result = response.json()
    if result["page"]["total_results"] != 1:
        return None
    return result["result"][0]["username"]


def distgit2fas(uri, config):
    distgit_hostname = re.escape(config["distgit_hostname"])
    m = re.search(f"^https?://{distgit_hostname}/user/([a-z][a-z0-9]+)$", uri)
    if m:
        return m.group(1)
    return uri


def krb2fas(name):
    if "/" not in name:
        return name
    return name.split("/")[0]


def validate_possible(possible, fields):
    fields_set = set(fields)
    if not fields_set.issubset(possible):
        raise KeyError(
            f"{fields_set.difference(possible)!r} are not possible fields. "
            f"Choose from {possible!r}"
        )


def validate_badge(required, possible, badge_dict):
    fields = frozenset(list(badge_dict.keys()))
    validate_possible(possible, fields)
    if required and not required.issubset(fields):
        raise ValueError(
            f"BadgeRule requires {required!r}. Missing {required.difference(fields)!r}"
        )


operators = frozenset(
    [
        "all",
        "any",
        "not",
    ]
)
lambdas = frozenset(
    [
        "lambda",
    ]
)

operator_lookup = {"any": any, "all": all, "not": lambda x: all([not item for item in x])}


class BadgeRule:
    required = frozenset(
        [
            "name",
            "image_url",
            "description",
            "creator",
            "discussion",
            "issuer_id",
            "trigger",
            "criteria",
        ]
    )

    possible = required.union(
        [
            "recipient",
            "recipient_nick2fas",
            "recipient_email2fas",
            "recipient_openid2fas",
            "recipient_github2fas",
            "recipient_distgit2fas",
            "recipient_krb2fas",
        ]
    )

    banned_usernames = frozenset(
        [
            "bodhi",
            "oscar",
            "apache",
            "koji",
            "bodhi",
            "taskotron",
        ]
    )

    def __init__(self, badge_dict, issuer_id, config, fasjson):
        validate_badge(self.required, self.possible, badge_dict)
        self._d = badge_dict
        self.issuer_id = issuer_id
        self.config = config
        self.fasjson = fasjson

        self.trigger = Trigger(self._d["trigger"], self)
        self.criteria = Criteria(self._d["criteria"], self)
        self.recipient_key = self._d.get("recipient")
        self.recipient_nick2fas = self._d.get("recipient_nick2fas")
        self.recipient_email2fas = self._d.get("recipient_email2fas")
        self.recipient_openid2fas = self._d.get("recipient_openid2fas")
        self.recipient_github2fas = self._d.get("recipient_github2fas")
        self.recipient_distgit2fas = self._d.get("recipient_distgit2fas")
        self.recipient_krb2fas = self._d.get("recipient_krb2fas")

    def setup(self, tahrir: TahrirDatabase):
        with tahrir.session.begin():
            self.badge_id = self._d["badge_id"] = tahrir.add_badge(
                name=self._d["name"],
                image=self._d["image_url"],
                desc=self._d["description"],
                criteria=self._d["discussion"],
                tags=",".join(self._d.get("tags", [])),
                issuer_id=self.issuer_id,
            )
            tahrir.session.commit()

    def __getitem__(self, key):
        return self._d[key]

    def __repr__(self):
        return f"<fedbadges.models.BadgeRule: {self._d!r}>"

    def matches(self, msg: Message, tahrir: TahrirDatabase):

        # First, do a lightweight check to see if the msg matches a pattern.
        if not self.trigger.matches(msg):
            return set()

        # Before proceeding further, let's see who would get this badge if
        # our more heavyweight checks matched up.  If the user specifies a
        # recipient_key, we can use that to extract the potential awardee.  If
        # that is not specified, we just use `msg2usernames`.
        if self.recipient_key:
            subs = construct_substitutions({"msg": msg.body})
            obj = format_args(self.recipient_key, subs)

            if isinstance(obj, (str, int, float)):
                obj = [obj]

            # On the way, it is possible for the fedmsg message to contain None
            # for "agent".  A problem here though is that None is not iterable,
            # so let's replace it with an equivalently empty iterable so code
            # further down doesn't freak out.  An instance of this is when a
            # user without a fas account comments on a bodhi update.
            if obj is None:
                obj = []

            # It is possible to recieve a list of dictionary containing the name
            # of the recipient, this is the case in the pagure's fedmsg.
            # In that case we create a new list containing the names taken from the
            # dictionnary.

            new_obj = get_pagure_authors(obj)
            if new_obj:
                obj = new_obj

            awardees = frozenset(obj)

            if self.recipient_nick2fas:
                awardees = frozenset([nick2fas(nick, self.fasjson) for nick in awardees])

            if self.recipient_email2fas:
                awardees = frozenset([email2fas(email, self.fasjson) for email in awardees])

            if self.recipient_openid2fas:
                awardees = frozenset([openid2fas(openid, self.config) for openid in awardees])

            if self.recipient_github2fas:
                awardees = frozenset(
                    [github2fas(uri, self.config, self.fasjson) for uri in awardees]
                )

            if self.recipient_distgit2fas:
                awardees = frozenset([distgit2fas(uri, self.config) for uri in awardees])

            if self.recipient_krb2fas:
                awardees = frozenset([krb2fas(uri) for uri in awardees])

            awardees = frozenset([e for e in awardees if e is not None])
        else:
            awardees = frozenset(msg.usernames)

        awardees = awardees.difference(self.banned_usernames)

        # Strip anyone who is an IP address
        awardees = frozenset(
            [
                user
                for user in awardees
                if not (user.startswith("192.168.") or user.startswith("10."))
            ]
        )

        # If no-one would get the badge by default, then no reason to waste
        # time doing any further checks.  No need to query the Tahrir DB.
        if not awardees:
            return awardees

        # Limit awardees to only those who do not already have this badge.
        awardees = frozenset(
            [
                user
                for user in awardees
                if not tahrir.assertion_exists(self.badge_id, f"{user}@fedoraproject.org")
                and not tahrir.person_opted_out(f"{user}@fedoraproject.org")
            ]
        )

        # If no-one would get the badge at this point, then no reason to waste
        # time doing any further checks.  No need to query datanommer.
        if not awardees:
            return awardees

        # Check our backend criteria -- likely, perform datanommer queries.
        try:
            if not self.criteria.matches(msg):
                return set()
        except OSError:
            log.exception("Failed checking criteria for rule %s", self.badge_id)
            return set()

        # Lastly, and this is probably most expensive.  Make sure the person
        # actually has a FAS account before we award anything.
        # https://github.com/fedora-infra/tahrir/issues/225
        awardees = set([u for u in awardees if user_exists_in_fas(self.fasjson, u)])

        return awardees


class AbstractComparator(metaclass=abc.ABCMeta):
    """Base class for shared behavior between trigger and criteria."""

    possible = required = frozenset()
    children = None

    def __init__(self, d, parent=None):
        validate_badge(self.required, self.possible, d)
        self._d = d
        self.parent = parent

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._d!r}>, a child of {self.parent!r}"

    @abc.abstractmethod
    def matches(self, msg):
        pass


class AbstractTopLevelComparator(AbstractComparator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls = type(self)

        if len(self._d) > 1:
            raise ValueError(
                "No more than one trigger allowed.  " "Use an operator, one of %r" % operators
            )
        self.attribute = next(iter(self._d))
        self.expected_value = self._d[self.attribute]

        # XXX - Check if we should we recursively nest Trigger/Criteria?

        # First, trick negation into thinking it is not a unary operator.
        if self.attribute == "not":
            self.expected_value = [self.expected_value]

        # Then, treat everything as if it accepts an arbitrary # of args.
        if self.attribute in operators:
            if not isinstance(self.expected_value, list):
                raise TypeError("Operators only accept lists, not %r" % type(self.expected_value))
            self.children = [cls(child, self) for child in self.expected_value]


class Trigger(AbstractTopLevelComparator):
    possible = (
        frozenset(
            [
                "topic",
                "category",
            ]
        )
        .union(operators)
        .union(lambdas)
    )

    @graceful(set())
    def matches(self, msg):
        # Check if we should just aggregate the results of our children.
        # Otherwise, we are a leaf-node doing a straightforward comparison.
        if self.children:
            return operator_lookup[self.attribute](child.matches(msg) for child in self.children)
        elif self.attribute == "lambda":
            return single_argument_lambda_factory(
                expression=self.expected_value, argument={"msg": msg.body}, name="msg"
            )
        elif self.attribute == "category":
            return msg.topic.split(".")[3] == self.expected_value
        elif self.attribute == "topic":
            return msg.topic.endswith(self.expected_value)
        else:
            raise RuntimeError(f"Unexpected attribute: {self.attribute}")


class Criteria(AbstractTopLevelComparator):
    possible = frozenset(
        [
            "datanommer",
        ]
    ).union(operators)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.children:
            # Then, by AbstractComparator rules, I am a leaf node.  Specialize!
            self._specialize()

    def _specialize(self):
        if self.attribute == "datanommer":
            self.specialization = DatanommerCriteria(self.expected_value)
        # TODO -- expand this with other "backends" as necessary
        # elif self.attribute == 'fas'
        else:
            raise RuntimeError("This should be impossible to reach.")

    @graceful(set())
    def matches(self, msg):
        if self.children:
            return operator_lookup[self.attribute](child.matches(msg) for child in self.children)
        else:
            return self.specialization.matches(msg)


class AbstractSpecializedComparator(AbstractComparator):
    pass


class DatanommerCriteria(AbstractSpecializedComparator):
    required = possible = frozenset(
        [
            "filter",
            "operation",
            "condition",
        ]
    )

    condition_callbacks = {
        "is greater than or equal to": lambda t, v: v >= t,
        "greater than or equal to": lambda t, v: v >= t,
        "greater than": lambda t, v: v > t,
        "is less than or equal to": lambda t, v: v <= t,
        "less than or equal to": lambda t, v: v <= t,
        "less than": lambda t, v: v < t,
        "equal to": lambda t, v: v == t,
        "is equal to": lambda t, v: v == t,
        "is not": lambda t, v: v != t,
        "is not equal to": lambda t, v: v != t,
        "lambda": single_argument_lambda_factory,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self._d["condition"]) > 1:
            conditions = list(self.condition_callbacks.keys())
            raise ValueError("No more than one condition allowed.  " "Use one of %r" % conditions)

        # Determine what arguments datanommer..grep accepts
        argspec = inspect.getfullargspec(datanommer.models.Message.grep)
        irrelevant = frozenset(["defer"])
        grep_arguments = frozenset(argspec.args[1:]).difference(irrelevant)

        # Validate the filter
        validate_possible(grep_arguments, self._d["filter"])

        # Validate the condition
        condition_key, condition_val = next(iter(self._d["condition"].items()))
        if condition_key not in self.condition_callbacks:
            raise KeyError(
                f"{condition_key!r} is not a valid condition key. "
                f"Use one of {list(self.condition_callbacks)!r}"
            )

        # Construct a condition callable for later
        self.condition = functools.partial(self.condition_callbacks[condition_key], condition_val)

    def _construct_query(self, msg):
        """Construct a datanommer query for this message.

        The "filter" section of this criteria object will be used.  It will
        first be formatted with any substitutions present in the incoming
        message.  This is used, for instance, to construct a query like "give
        me all the messages bearing the same topic as the message that just
        arrived".
        """
        subs = construct_substitutions({"msg": msg.body})
        kwargs = format_args(copy.copy(self._d["filter"]), subs)
        kwargs = recursive_lambda_factory(kwargs, {"msg": msg.body}, name="msg")

        # It is possible to recieve a list of dictionary containing the name
        # of the recipient, this is the case in the pagure's fedmsg.
        # In that case we create a new list containing the names taken from the
        # dictionnary.
        if kwargs.get("users") is not None:
            for item in kwargs["users"]:
                if isinstance(item, list):
                    kwargs["users"] = item
            users = get_pagure_authors(kwargs["users"])
            if users:
                kwargs["users"] = users
        kwargs["defer"] = True
        total, pages, query = datanommer.models.Message.grep(**kwargs)
        return total, pages, query

    def _format_lambda_operation(self, msg):
        """Format the string representation of a lambda operation.

        The lambda operation can be formatted here to include strings that
        appear in the message being evaluated like
        %(msg.comment.update_submitter)s.  Placeholders like that will have
        their value substituted with whatever appears in the incoming message.
        """
        subs = construct_substitutions({"msg": msg.body})
        operation = format_args(copy.copy(self._d["operation"]), subs)
        return operation["lambda"]

    def matches(self, msg: Message):
        """A datanommer criteria check is composed of three steps.

        - A datanommer query is constructed by combining our yaml definition
          with the incoming fedmsg message that triggered us.
        - An operation in python is constructed by comining our yaml definition
          with the incoming fedmsg message that triggered us.  That operation
          is then executed against the datanommer query object.
        - A condition, derived from our yaml definition, is evaluated with the
          result of the operation from the previous step and is returned.
        """
        total, pages, query = self._construct_query(msg)
        if self._d["operation"] == "count":
            result = total
        elif isinstance(self._d["operation"], dict):
            expression = self._format_lambda_operation(msg)
            result = single_argument_lambda_factory(
                expression=expression, argument=query, name="query"
            )
        else:
            operation = getattr(query, self._d["operation"])
            result = operation()
        return self.condition(result)
