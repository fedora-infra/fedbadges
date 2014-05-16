import unittest
import mock
from nose.tools import raises, eq_

import fedbadges.rules


class TestCriteriaPkgdbWeirdness(unittest.TestCase):
    @raises(KeyError)
    def test_underspecified_criteria(self):
        """ Test that an error is raised when condition is missing. """
        criteria = fedbadges.rules.Criteria(dict(
            pkgdb={
                "owns": {
                    "user": "ralph",
                    # You must specify a list of packages here
                },
            }
        ))

    @raises(ValueError)
    def test_malformed_owns(self):
        """ Test that an error is raised for malformed owns entries """
        criteria = fedbadges.rules.Criteria(dict(
            pkgdb={
                "owns": "wat",  # this must be a dict.
            }
        ))

    @raises(ValueError)
    def test_malformed_not_a_list(self):
        """ Test that an error is raised for malformed owns entries """
        criteria = fedbadges.rules.Criteria(dict(
            pkgdb={
                "owns": {
                    "user": "ralph",
                    "packages": "not a list",
                },
            }
        ))


class TestCriteriaPkgdbOwns(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria(dict(
            pkgdb={
                "owns": {
                    "user": "ralph",
                    "packages": [
                        "%(some_package)s",
                    ],
                },
            }
        ))
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
            some_package="pkgwat",
        )

    def test_basic_ownership_miss(self):
        expectation = False

        with mock.patch('fedbadges.rules.get_pkgdb_packages_for') as f:
            f.return_value = ['fedmsg', 'nethack']
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                config=fedbadges.rules.fedmsg_config,
                user="ralph",
            )

    def test_basic_ownership_hit(self):
        expectation = True

        with mock.patch('fedbadges.rules.get_pkgdb_packages_for') as f:
            f.return_value = ['pkgwat', 'fedmsg', 'nethack']
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                config=fedbadges.rules.fedmsg_config,
                user="ralph",
            )


class TestCriteriaNegatedPkgdbOwns(unittest.TestCase):
    def setUp(self):
        self.criteria = fedbadges.rules.Criteria({
            "not": dict(pkgdb={
                "owns": {
                    "user": "ralph",
                    "packages": ["%(some_package)s"],
                },
            })})
        self.message = dict(
            topic="org.fedoraproject.dev.something.sometopic",
            some_package="pkgwat",
        )

    def test_negated_ownership_hit(self):
        expectation = False

        with mock.patch('fedbadges.rules.get_pkgdb_packages_for') as f:
            f.return_value = ['pkgwat', 'fedmsg', 'nethack']
            result = self.criteria.matches(self.message)
            eq_(result, expectation)
            f.assert_called_once_with(
                config=fedbadges.rules.fedmsg_config,
                user="ralph",
            )
