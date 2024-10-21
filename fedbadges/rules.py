""" Models for fedbadges.

The primary thing here is a "BadgeRule" which is an in-memory working
abstraction of the trigger and criteria required to award a badge.

Authors:    Ralph Bean
"""

import abc
import datetime
import functools
import inspect
import logging
import time
from itertools import chain

import datanommer.models
import redis
from dogpile.lock import Lock, NeedRegenerationException
from fedora_messaging.api import Message
from tahrir_api.dbapi import TahrirDatabase

from fedbadges.cached import cache
from fedbadges.fas import distgit2fas, krb2fas, openid2fas
from fedbadges.utils import (
    # These are all in-process utilities
    graceful,
    json_hash,
    lambda_factory,
    list_of_lambdas,
    single_argument_lambda,
    single_argument_lambda_factory,
)


log = logging.getLogger(__name__)


def validate_possible(possible, fields):
    fields_set = set(fields)
    if not fields_set.issubset(possible):
        raise ValueError(
            f"{fields_set.difference(possible)!r} are not possible fields. "
            f"Choose from {possible!r}"
        )


def validate_required(required, fields):
    if required and not required.issubset(fields):
        raise ValueError(
            f"Required fields are {required!r}. Missing {required.difference(fields)!r}"
        )


def validate_fields(required, possible, value: dict):
    fields = set(list(value.keys()))
    validate_possible(possible, fields)
    validate_required(required, fields)


operators = {"any": any, "all": all, "not": lambda x: all(not item for item in x)}
lambdas = frozenset(
    [
        "lambda",
    ]
)


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
        ]
    )

    possible = required.union(
        [
            "condition",
            "previous",
            "recipient",
            "recipient_nick2fas",
            "recipient_email2fas",
            "recipient_openid2fas",
            "recipient_github2fas",
            "recipient_distgit2fas",
            "recipient_krb2fas",
        ]
    )

    def __init__(self, badge_dict, issuer_id, config, fasjson):
        try:
            validate_fields(self.required, self.possible, badge_dict)
        except ValueError as e:
            raise ValueError(f"Validation failed for {badge_dict['name']}: {e}") from e
        self._d = badge_dict
        self.issuer_id = issuer_id
        self.config = config
        self.fasjson = fasjson

        self.trigger = Trigger(self._d["trigger"], self)
        if "condition" in self._d:
            self.condition = Condition(self._d["condition"], self)
        else:
            # Default condition: always true (the rule trigger is sufficient)
            self.condition = lambda v: True

        if "previous" in self._d:
            self.previous = DatanommerCounter(self._d["previous"], self)
        else:
            # By default: only the current message
            self.previous = None

        # self.recipient_key = self._d.get("recipient")
        self.recipient_getter = single_argument_lambda_factory(
            # If the user specifies a recipient, we can use that to extract the awardees.
            # If that is not specified, we just use `message.agent_name`.
            self._d.get("recipient", "message.agent_name"),
            name="message",
        )
        # TODO: make a recipient_converter list in the yaml
        self.recipient_nick2fas = self._d.get("recipient_nick2fas")
        self.recipient_email2fas = self._d.get("recipient_email2fas")
        self.recipient_openid2fas = self._d.get("recipient_openid2fas")
        self.recipient_github2fas = self._d.get("recipient_github2fas")
        self.recipient_distgit2fas = self._d.get("recipient_distgit2fas")
        self.recipient_krb2fas = self._d.get("recipient_krb2fas")

    def setup(self, tahrir: TahrirDatabase):
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

    def _get_candidates(self, msg: Message, tahrir: TahrirDatabase):
        try:
            candidates = self.recipient_getter(message=msg)
        except KeyError as e:
            log.debug("Could not get the recipients. KeyError: %s", e)
            return frozenset()

        if isinstance(candidates, (str, int, float)):
            candidates = [candidates]

        # On the way, it is possible for the fedmsg message to contain None
        # for "agent".  A problem here though is that None is not iterable,
        # so let's replace it with an equivalently empty iterable so code
        # further down doesn't freak out.  An instance of this is when a
        # user without a fas account comments on a bodhi update.
        if candidates is None:
            candidates = []

        candidates = frozenset(candidates)

        if self.recipient_nick2fas:
            candidates = frozenset([self.fasjson.search_ircnick(nick) for nick in candidates])

        if self.recipient_email2fas:
            candidates = frozenset([self.fasjson.search_email(email) for email in candidates])

        if self.recipient_openid2fas:
            candidates = frozenset([openid2fas(openid, self.config) for openid in candidates])

        if self.recipient_github2fas:
            candidates = frozenset([self.fasjson.search_github(uri) for uri in candidates])

        if self.recipient_distgit2fas:
            candidates = frozenset([distgit2fas(uri, self.config) for uri in candidates])

        if self.recipient_krb2fas:
            candidates = frozenset([krb2fas(uri) for uri in candidates])

        # Remove None
        candidates = frozenset([e for e in candidates if e is not None])

        # Skipped usernames
        candidates = candidates.difference(frozenset(self.config.get("skip_users", [])))

        # Strip anyone who is an IP address
        candidates = frozenset(
            [
                user
                for user in candidates
                if not (user.startswith("192.168.") or user.startswith("10."))
            ]
        )

        # Limit candidates to only those who do not already have this badge.
        candidates = frozenset(
            [
                user
                for user in candidates
                if not tahrir.assertion_exists(self.badge_id, f"{user}@fedoraproject.org")
                and not tahrir.person_opted_out(f"{user}@fedoraproject.org")
            ]
        )

        # Make sure the person actually has a FAS account before we award anything.
        # https://github.com/fedora-infra/tahrir/issues/225
        candidates = set([u for u in candidates if self.fasjson.user_exists(u)])

        return candidates

    def _get_current_value(self, candidate: str, previous_count_fn, tahrir: TahrirDatabase):
        lock_key = f"messages_count|{self.badge_id}|{candidate}"
        user_email = f"{candidate}@{self.config['email_domain']}"

        def get_value():
            value = tahrir.get_current_value(self.badge_id, user_email)
            if value is None:
                raise NeedRegenerationException()
            # The dogpile.lock API ask us to return a (value, creation time) tuple
            return value, time.time()

        def gen_value():
            # Ask Datanommer. We'll add the current message later, but it's already in DN,
            # so substract it now.
            value = previous_count_fn(candidate) - 1
            # The dogpile.lock API ask us to return a (value, creation time) tuple
            return value, time.time()

        # Use a distributed lock to avoid two consumers processing the same rule for the same
        # candidate at the same time and overwriting each other's values.
        try:
            with Lock(
                cache.backend.get_mutex(lock_key),
                gen_value,
                get_value,
                expiretime=None,
            ) as value:
                # Add one (the current message)
                new_value = value + 1
                # Store the value in the DB for next time
                tahrir.set_current_value(self.badge_id, user_email, new_value)
                tahrir.session.commit()
                return new_value
        except redis.exceptions.LockNotOwnedError:
            # This happens when the get_previous_fn() call lasted longer that the maximum redis lock
            # time. In this case, the value has been computed and stored in the DB, but dogpile just
            # failed to release the lock. Just try again, the value should be there already.
            log.debug(
                "Oops, getting the cached messages count of rule %s for user %s took too long for "
                "the cache lock. Retrying. It should be fast now.",
                self.badge_id,
                candidate,
            )
            return self._get_current_value(candidate, previous_count_fn, tahrir)

    def matches(self, msg: Message, tahrir: TahrirDatabase):
        # First, do a lightweight check to see if the msg matches a pattern.
        if not self.trigger.matches(msg):
            # log.debug(f"Rule {self.badge_id} does not trigger")
            return frozenset()

        log.debug("Checking match for rule %s", self.badge_id)
        # Before proceeding further, let's see who would get this badge if
        # our more heavyweight checks matched up.

        candidates = self._get_candidates(msg, tahrir)
        log.debug("Candidates: %r", candidates)

        # If no-one would get the badge at this point, then no reason to waste
        # time doing any further checks.  No need to query datanommer.
        if not candidates:
            return frozenset()

        if self.previous:
            previous_count_fn = functools.partial(self.previous.count, msg)
        else:
            previous_count_fn = lambda candidate: 1  # noqa: E731

        # Check our backend criteria -- possibly, perform datanommer queries.
        try:
            awardees = set()
            for candidate in candidates:
                messages_count = self._get_current_value(candidate, previous_count_fn, tahrir)
                log.debug(
                    "Rule %s: message count for %s is %s", self.badge_id, candidate, messages_count
                )
                if self.condition(messages_count):
                    awardees.add(candidate)
        except OSError:
            log.exception("Failed checking criteria for rule %s", self.badge_id)
            return frozenset()

        return awardees


class AbstractChild:
    """Base class for shared behavior between trigger and criteria."""

    possible = required = frozenset()
    children = None

    def __init__(self, d, parent=None):
        validate_fields(self.required, self.possible, d)
        self._d = d
        self.parent = parent

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._d!r}>, a child of {self.parent!r}"

    def get_top_parent(self):
        parent = self.parent
        while hasattr(parent, "parent") and parent.parent is not None:
            parent = parent.parent
        return parent


class AbstractComparator(AbstractChild, metaclass=abc.ABCMeta):
    """Base class for shared behavior between trigger and criteria."""

    @abc.abstractmethod
    def matches(self, msg):
        pass


class AbstractTopLevelComparator(AbstractComparator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls = type(self)

        if len(self._d) > 1:
            raise ValueError(
                f"No more than one trigger allowed. Use an operator, one of {', '.join(operators)}"
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
                raise TypeError(f"Operators only accept lists, not {type(self.expected_value)}")
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
            return operators[self.attribute](child.matches(msg) for child in self.children)
        elif self.attribute == "lambda":
            func = single_argument_lambda_factory(
                expression=self.expected_value,
                name="message",
            )
            try:
                return func(message=msg)
            except KeyError as e:
                log.debug("Could not check the trigger. KeyError: %s", e)
                # The message body wasn't what we expected: no match
                return False
        elif self.attribute == "category":
            return msg.topic.split(".")[3] == self.expected_value
        elif self.attribute == "topic":
            return msg.topic.endswith(self.expected_value)
        else:
            raise RuntimeError(f"Unexpected attribute: {self.attribute}")


class Condition(AbstractChild):

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
        "lambda": single_argument_lambda,
    }
    possible = frozenset(condition_callbacks.keys())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(self._d) > 1:
            raise ValueError(
                f"No more than one condition allowed. Use one of {list(self.condition_callbacks)}"
            )
        # Validate the condition
        condition_name, threshold = next(iter(self._d.items()))
        if condition_name not in self.condition_callbacks:
            raise ValueError(
                f"{condition_name!r} is not a valid condition key. "
                f"Use one of {list(self.condition_callbacks)!r}"
            )

        # Construct a condition callable for later
        self._condition = functools.partial(self.condition_callbacks[condition_name], threshold)

    def __call__(self, value):
        return self._condition(value)


class DatanommerCounter(AbstractChild):
    required = possible = frozenset(
        [
            "filter",
            "operation",
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine what arguments datanommer.models.Message.grep accepts
        argspec = inspect.getfullargspec(datanommer.models.Message.make_query)
        grep_arguments = set(argspec.args[1:])
        grep_arguments.update({"rows_per_page", "page", "order"})
        # Validate the filter and compile its getter
        validate_possible(grep_arguments, self._d["filter"])
        self._filter_getters = self._build_filter_getters()
        # Compile the operation if it's a lambda
        if isinstance(self._d["operation"], dict) and list(self._d["operation"]) == ["lambda"]:
            expression = self._d["operation"]["lambda"]
            self._operation_func = lambda_factory(
                expression=expression, args=("message", "results")
            )
        elif self._d["operation"] != "count":
            raise ValueError("Datanommer operations are either 'count' or a lambda")

        top_parent = self.get_top_parent()
        self.fasjson = getattr(top_parent, "fasjson", None)

    def _build_filter_getters(self):
        _getter_arguments = ("message", "recipient")
        _getters = {}
        for argument, value in self._d["filter"].items():
            if isinstance(value, list):
                _getter = list_of_lambdas(value, _getter_arguments)
            else:
                _getter = lambda_factory(expression=value, args=_getter_arguments)
            _getters[argument] = _getter
        return _getters

    def _make_query(self, search_kwargs):
        log.debug("Making datanommer query: %r", search_kwargs)
        _search_kwargs = search_kwargs.copy()
        _search_kwargs["defer"] = True
        _search_kwargs.setdefault("rows_per_page", 0)
        total, pages, query = datanommer.models.Message.grep(**_search_kwargs)
        return total, pages, query

    def _get_start(self, search_kwargs):
        # This is an optimization: don't search before the user was created
        if self.fasjson is None:
            return None

        user_related_args = ("users", "agents")
        if not any(arg in search_kwargs for arg in user_related_args):
            return None

        def _get_user_creation_time(username):
            log.debug("Getting creation time for: %r", username)
            user = self.fasjson.get_user(username)
            if user is None:
                return None
            return datetime.datetime.fromisoformat(user["creation"])

        start = None
        for username in chain(*[search_kwargs.get(arg, []) for arg in user_related_args]):
            user_creation_time = _get_user_creation_time(username)
            if user_creation_time is None:
                continue
            # start looking the day before, to avoid messing up with timezones
            user_start = user_creation_time - datetime.timedelta(days=1)
            # use the earliest creation time of all selected users because they are ORed
            if start is None or user_start < start:
                start = user_start
        return start

    def _query_with_operation(
        self, message: Message, search_kwargs: dict[str, int | str | list[str]]
    ):
        if "start" not in search_kwargs:
            start = self._get_start(search_kwargs)
            if start is not None:
                search_kwargs["start"] = start
                if "end" not in search_kwargs:
                    # user creation time is naive, let's keep the end dt naive as well
                    # also, the datanommer column is currently naive, so, let's be consistent
                    search_kwargs["end"] = datetime.datetime.now()

        total, _pages, query = self._make_query(search_kwargs)
        if self._d["operation"] == "count":
            return total
        elif isinstance(self._d["operation"], dict):
            query_results = datanommer.models.session.scalars(query).all()
            try:
                return self._operation_func(message=message, results=query_results)
            except KeyError as e:
                log.debug("Could not run the lambda. KeyError: %s", e)
                return 0

    def count(self, msg: Message, candidate: str):
        try:
            search_kwargs = {
                search_key: getter(message=msg, recipient=candidate)
                for search_key, getter in self._filter_getters.items()
            }
        except KeyError as e:
            log.debug("Could not compute the search kwargs. KeyError: %s", e)
            return 0
        # Cache for other rules analyzing this message
        cache_key = f"{msg.id}|{json_hash(search_kwargs)}|{json_hash(self._d['operation'])}"
        return cache.get_or_create(
            cache_key, self._query_with_operation, creator_args=((msg, search_kwargs), {})
        )
