import unittest
from nose.tools import eq_

from fedbadges.utils import (
    construct_substitutions,
    format_args,
    single_argument_lambda_factory,
)


class TestLambdaFactory(unittest.TestCase):
    def test_basic(self):
        expression = "value + 2"
        target = 4
        actual = single_argument_lambda_factory(expression, 2)
        eq_(actual, target)


class TestSubsitutions(unittest.TestCase):
    def test_basic(self):
        msg = dict(a=dict(b=dict(c=42)))
        target = {"a.b.c": 42}
        actual = construct_substitutions(msg)
        eq_(actual, target)

    def test_real(self):
        msg = {
            "i": 2,
            "msg": {
                "thread": {
                    "tagnames": [
                        "town"
                    ],
                    "pk": 2,
                    "title": "alskdjflaksjdf lakjsf a"
                },
                "created": False,
                "timestamp": 1359947640.0,
                "topmost_post_id": 2,
                "agent": "ralph",
                "newly_mentioned_users": [],
                "diff": "<p>alskdfj... the diff is actually here",
                "post": {
                    "vote_up_count": 0,
                    "text": "alskdfjalskdjf alkjasdalskdjf ...",
                    "summary": "alskdfjalskdjf alkjasdalskdjf ...",
                    "comment_count": 0,
                    "vote_down_count": 0,
                    "pk": 2,
                    "post_type": "question"
                }
            },
            "topic": "org.fedoraproject.dev.askbot.post.edit",
            "username": "threebean",
            "timestamp": 1359947640.986208
        }
        target = {
            'i': 2,
            'msg.agent': 'ralph',
            'msg.created': False,
            'msg.diff': '<p>alskdfj... the diff is actually here',
            'msg.newly_mentioned_users': [],
            'msg.post.comment_count': 0,
            'msg.post.pk': 2,
            'msg.post.post_type': 'question',
            'msg.post.summary': 'alskdfjalskdjf alkjasdalskdjf ...',
            'msg.post.text': 'alskdfjalskdjf alkjasdalskdjf ...',
            'msg.post.vote_down_count': 0,
            'msg.post.vote_up_count': 0,
            'msg.thread.pk': 2,
            'msg.thread.tagnames': ['town'],
            'msg.thread.title': 'alskdjflaksjdf lakjsf a',
            'msg.timestamp': 1359947640.0,
            'msg.topmost_post_id': 2,
            'timestamp': 1359947640.986208,
            'topic': 'org.fedoraproject.dev.askbot.post.edit',
            'username': 'threebean',
        }
        actual = construct_substitutions(msg)
        eq_(actual, target)


class TestFormatArgs(unittest.TestCase):
    def test_simple(self):
        subs = {
            "foo.bar.baz": "value",
        }
        obj = {
            "something should be": "%(foo.bar.baz)s",
        }
        target = {
            "something should be": "value",
        }
        actual = format_args(obj, subs)
        eq_(actual, target)

    def test_list(self):
        subs = {
            "foo.bar.baz": "value",
        }
        obj = {
            "something should be": [
                "%(foo.bar.baz)s",
                "or this",
            ]
        }
        target = {
            "something should be": [
                "value",
                "or this",
            ]
        }
        actual = format_args(obj, subs)
        eq_(actual, target)

    def test_numeric(self):
        subs = {
            "foo.bar.baz": 42,
        }
        obj = {
            "something should be": "%(foo.bar.baz)i",
        }
        target = {
            "something should be": 42,
        }
        actual = format_args(obj, subs)
        eq_(actual, target)

    def test_nested(self):
        subs = {
            "wat": "another",
        }
        obj = {
            "one": {
                "thing": {
                    "leads": {
                        "to": "%(wat)s",
                        "most": "of the time",
                    }
                }
            }
        }
        target = {
            "one": {
                "thing": {
                    "leads": {
                        "to": "another",
                        "most": "of the time",
                    }
                }
            }
        }
        actual = format_args(obj, subs)
        eq_(actual, target)
