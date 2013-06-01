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
        target = {"a_b_c": 42}
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
            'msg_agent': 'ralph',
            'msg_created': False,
            'msg_diff': '<p>alskdfj... the diff is actually here',
            'msg_newly_mentioned_users': [],
            'msg_post_comment_count': 0,
            'msg_post_pk': 2,
            'msg_post_post_type': 'question',
            'msg_post_summary': 'alskdfjalskdjf alkjasdalskdjf ...',
            'msg_post_text': 'alskdfjalskdjf alkjasdalskdjf ...',
            'msg_post_vote_down_count': 0,
            'msg_post_vote_up_count': 0,
            'msg_thread_pk': 2,
            'msg_thread_tagnames': ['town'],
            'msg_thread_title': 'alskdjflaksjdf lakjsf a',
            'msg_timestamp': 1359947640.0,
            'msg_topmost_post_id': 2,
            'timestamp': 1359947640.986208,
            'topic': 'org.fedoraproject.dev.askbot.post.edit',
            'username': 'threebean',
        }
        actual = construct_substitutions(msg)
        eq_(actual, target)


class TestFormatArgs(unittest.TestCase):
    def test_simple(self):
        subs = {
            "foo_bar_baz": "value",
        }
        obj = {
            "something should be": "{foo_bar_baz}",
        }
        target = {
            "something should be": "value",
        }
        actual = format_args(obj, subs)
        eq_(actual, target)

    def test_list(self):
        subs = {
            "foo_bar_baz": "value",
        }
        obj = {
            "something should be": [
                "{foo_bar_baz}",
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

    # XXX - This would be cool.
    #def test_numeric(self):
    #    subs = {
    #        "foo_bar_baz": 42,
    #    }
    #    obj = {
    #        "something should be": "{foo_bar_baz}",
    #    }
    #    target = {
    #        "something should be": 42,
    #    }
    #    actual = format_args(obj, subs)
    #    eq_(actual, target)

    def test_nested(self):
        subs = {
            "wat": "another",
        }
        obj = {
            "one": {
                "thing": {
                    "leads": {
                        "to": "{wat}",
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
