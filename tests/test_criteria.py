import unittest

from nose.tools import raises

import fedbadges.models


class TestCriteriaMatching(unittest.TestCase):
    @raises(ValueError)
    def test_malformed_criteria(self):
        criteria = fedbadges.models.Criteria(dict(
            watwat="does not exist",
        ))

    # TODO - mock out datanommer to test real criteria
