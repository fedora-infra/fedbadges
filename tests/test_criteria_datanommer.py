import unittest
import mock
from nose.tools import raises, eq_

import fedbadges.rules


class TestCriteriaMatching(unittest.TestCase):
    @raises(KeyError)
    def test_malformed_criteria(self):
        """Test that an error is raised when nonsense is provided."""
        criteria = fedbadges.rules.Criteria(
            dict(
                watwat="does not exist",
            )
        )

    @raises(ValueError)
    def test_underspecified_criteria(self):
        """Test that an error is raised when condition is missing."""
        criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {"topics": ["%(topic)s"], "wat": "baz"},
                    "operation": "count",
                }
            )
        )

    @raises(KeyError)
    def test_malformed_filter(self):
        """Test that an error is raised for malformed filters"""
        criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {"topics": ["%(topic)s"], "wat": "baz"},
                    "operation": "count",
                    "condition": {
                        "greater than or equal to": 500,
                    },
                }
            )
        )


class TestCriteriaCountGreaterThanOrEqualTo(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "topics": ["%(topic)s"],
                    },
                    "operation": "count",
                    "condition": {
                        "greater than or equal to": 500,
                    },
                }
            )
        )
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
        )

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_basic_datanommer_query_undershoot(self):
        self.returned_count = 499
        expectation = False

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                topics=["org.fedoraproject.dev.something.sometopic"],
                defer=True,
            )

    def test_basic_datanommer_query_spot_on(self):
        self.returned_count = 500
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                topics=["org.fedoraproject.dev.something.sometopic"],
                defer=True,
            )

    def test_basic_datanommer_query_overshoot(self):
        self.returned_count = 501
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                topics=["org.fedoraproject.dev.something.sometopic"],
                defer=True,
            )


class TestCriteriaLambdaConditions(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "topics": ["%(topic)s"],
                    },
                    "operation": "count",
                    "condition": {
                        "lambda": "value >= 500",
                    },
                }
            )
        )
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
        )

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_datanommer_with_lambda_condition_query_undershoot(self):
        self.returned_count = 499
        expectation = False

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_with_lambda_condition_query_spot_on(self):
        self.returned_count = 500
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_with_lambda_condition_query_overshoot(self):
        self.returned_count = 501
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)


class TestCriteriaLambdaOperationWithFormatting(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "topics": ["%(topic)s"],
                    },
                    "operation": {
                        "lambda": "query.count() == %(msg.some_value)s",
                    },
                    "condition": {
                        "lambda": "value",
                    },
                }
            )
        )
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
            msg=dict(
                some_value=5,
            ),
        )

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_datanommer_formatted_operations_undershoot(self):
        self.returned_count = 4
        expectation = False

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_formatted_operations_overshoot(self):
        self.returned_count = 6
        expectation = False

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_formatted_operations_righton(self):
        self.returned_count = 5
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)


class TestCriteriaLambdaOperationsAndConditions(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "topics": ["%(topic)s"],
                    },
                    "operation": {
                        "lambda": "query.count() - 5",
                    },
                    "condition": {
                        "lambda": "value >= 495",
                    },
                }
            )
        )
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
        )

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_datanommer_with_lambda_operation_query_undershoot(self):
        self.returned_count = 499
        expectation = False

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_with_lambda_operation_query_spot_on(self):
        self.returned_count = 500
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)

    def test_datanommer_with_lambda_operation_query_overshoot(self):
        self.returned_count = 501
        expectation = True

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = self.returned_count, 1, self.mock_query
            result = self.criteria.matches(self.message)
            eq_(result, expectation)


class TestCriteriaLambdaFilters(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "users": {
                            "lambda": "[u for u in fedmsg.meta.msg2usernames(msg)"
                            " if not u in ['bodhi', 'oscar']]",
                        }
                    },
                    "operation": "count",
                    "condition": {
                        "greater than or equal to": 0,
                    },
                }
            )
        )

        # Here we use a real message so we can test fedmsg.meta integration
        self.message = {
            "i": 1,
            "timestamp": 1368046115.802794,
            "topic": "org.fedoraproject.prod.trac.git.receive",
            "msg": {
                "commit": {
                    "username": "ralph",
                    "stats": {
                        "files": {"README.rst": {"deletions": 0, "lines": 1, "insertions": 1}},
                        "total": {"deletions": 0, "files": 1, "insertions": 1, "lines": 1},
                    },
                    "name": "Ralph Bean",
                    "rev": "24bcd20d08a68320f82951ce20959bc6a1a6e79c",
                    "agent": "ralph",
                    "summary": "Another commit to test fedorahosted fedmsg.",
                    "repo": "moksha",
                    "branch": "dev",
                    "message": "Another commit to test fedorahosted fedmsg.\n",
                    "email": "rbean@redhat.com",
                }
            },
        }

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_datanommer_with_lambda_filter(self):
        self.returned_count = 0

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, self.mock_query
            result = self.criteria.matches(self.message)
            f.assert_called_once_with(users=["ralph"], defer=True)


class TestCriteriaDottedFilter(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(
            dict(
                datanommer={
                    "filter": {
                        "users": [
                            "%(msg.commit.username)s",
                        ]
                    },
                    "operation": "count",
                    "condition": {
                        "greater than or equal to": 0,
                    },
                }
            )
        )

        # Here we use a real message so we can test fedmsg.meta integration
        self.message = {
            "i": 1,
            "timestamp": 1368046115.802794,
            "topic": "org.fedoraproject.prod.trac.git.receive",
            "msg": {
                "commit": {
                    "username": "ralph",
                    "stats": {
                        "files": {"README.rst": {"deletions": 0, "lines": 1, "insertions": 1}},
                        "total": {"deletions": 0, "files": 1, "insertions": 1, "lines": 1},
                    },
                    "name": "Ralph Bean",
                    "rev": "24bcd20d08a68320f82951ce20959bc6a1a6e79c",
                    "agent": "ralph",
                    "summary": "Another commit to test fedorahosted fedmsg.",
                    "repo": "moksha",
                    "branch": "dev",
                    "message": "Another commit to test fedorahosted fedmsg.\n",
                    "email": "rbean@redhat.com",
                }
            },
        }

        class MockQuery(object):
            def count(query):
                return self.returned_count

        self.mock_query = MockQuery()

    def test_datanommer_with_lambda_filter(self):
        self.returned_count = 0

        with mock.patch("datanommer.models.Message.grep") as f:
            f.return_value = None, None, self.mock_query
            result = self.criteria.matches(self.message)
            f.assert_called_once_with(users=["ralph"], defer=True)
