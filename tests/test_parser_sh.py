#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import datetime
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from sortinghat.db.model import UniqueIdentity, Organization, Domain
from sortinghat.exceptions import InvalidFormatError
from sortinghat.parsing.sh import SortingHatParser, SortingHatOrganizationsParser


SH_INVALID_JSON_FORMAT_ERROR = "invalid json format\. Expecting ',' delimiter"
SH_IDS_MISSING_KEYS_ERROR = "Attribute uuid not found"
SH_IDS_DATETIME_ERROR = "invalid date format: 2100-01-32T00:00:00"
SH_ORGS_MISSING_KEYS_ERROR = "Attribute is_top not found"
SH_ORGS_IS_TOP_ERROR = "'is_top' must have a bool value"

ORGS_INVALID_JSON_FORMAT_ERROR = "invalid json format. Expecting object"
ORGS_MISSING_KEYS_ERROR = "Attribute is_top not found"
ORGS_IS_TOP_ERROR = "'is_top' must have a bool value"
ORGS_STREAM_INVALID_ERROR = "stream cannot be empty or None"


class TestBaseCase(unittest.TestCase):
    """Defines common methods for unit tests"""

    def read_file(self, filename):
        with open(filename, 'r') as f:
            content = f.read().decode('UTF-8')
        return content


class TestSortingHatParser(TestBaseCase):
    """Test SortingHat parser with some inputs"""

    def test_valid_identities_stream(self):
        """Check whether it parsers identities section from a valid stream"""

        stream = self.read_file('data/sortinghat_valid.json')

        parser = SortingHatParser(stream)
        uids = parser.identities

        # Check parsed identities
        self.assertEqual(len(uids), 3)

        # 00000 identity
        uid = uids[0]
        self.assertIsInstance(uid, UniqueIdentity)
        self.assertEqual(uid.uuid, '0000000000000000000000000000000000000000')
        self.assertEqual(len(uid.enrollments), 0)
        self.assertEqual(len(uid.identities), 0)

        # John Smith
        uid = uids[1]
        self.assertIsInstance(uid, UniqueIdentity)
        self.assertEqual(uid.uuid, '03e12d00e37fd45593c49a5a5a1652deca4cf302')

        ids = uid.identities
        self.assertEqual(len(ids), 2)

        id0 = ids[0]
        self.assertEqual(id0.id, '03e12d00e37fd45593c49a5a5a1652deca4cf302')
        self.assertEqual(id0.name, 'John Smith')
        self.assertEqual(id0.email, 'jsmith@example.com')
        self.assertEqual(id0.username, 'jsmith')
        self.assertEqual(id0.source, 'scm')

        id1 = ids[1]
        self.assertEqual(id1.id, '75d95d6c8492fd36d24a18bd45d62161e05fbc97')
        self.assertEqual(id1.name, 'John Smith')
        self.assertEqual(id1.email, 'jsmith@example.com')
        self.assertEqual(id1.username, None)
        self.assertEqual(id1.source, 'scm')

        enrollments = uid.enrollments
        self.assertEqual(len(enrollments), 1)

        rol0 = enrollments[0]
        self.assertIsInstance(rol0.organization, Organization)
        self.assertEqual(rol0.organization.name, 'Example')
        self.assertEqual(rol0.start, datetime.datetime(1900, 1, 1, 0, 0))
        self.assertEqual(rol0.end, datetime.datetime(2100, 1, 1, 0, 0))

        # Jane Roe
        uid = uids[2]
        self.assertIsInstance(uid, UniqueIdentity)
        self.assertEqual(uid.uuid, '52e0aa0a14826627e633fd15332988686b730ab3')

        ids = uid.identities
        self.assertEqual(len(ids), 3)

        id0 = ids[0]
        self.assertEqual(id0.id, '52e0aa0a14826627e633fd15332988686b730ab3')
        self.assertEqual(id0.name, 'Jane Roe')
        self.assertEqual(id0.email, 'jroe@example.com')
        self.assertEqual(id0.username, 'jroe')
        self.assertEqual(id0.source, 'scm')

        id1 = ids[1]
        self.assertEqual(id1.id, 'cbfb7bd31d556322c640f5bc7b31d58a12b15904')
        self.assertEqual(id1.name, None)
        self.assertEqual(id1.email, 'jroe@bitergia.com')
        self.assertEqual(id1.username, None)
        self.assertEqual(id1.source, 'unknown')

        id2 = ids[2]
        self.assertEqual(id2.id, 'fef873c50a48cfc057f7aa19f423f81889a8907f')
        self.assertEqual(id2.name, None)
        self.assertEqual(id2.email, 'jroe@example.com')
        self.assertEqual(id2.username, None)
        self.assertEqual(id2.source, 'scm')

        enrollments = uid.enrollments
        self.assertEqual(len(enrollments), 3)

        rol0 = enrollments[0]
        self.assertIsInstance(rol0.organization, Organization)
        self.assertEqual(rol0.organization.name, 'Bitergia')
        self.assertEqual(rol0.start, datetime.datetime(1999, 1, 1, 0, 0))
        self.assertEqual(rol0.end, datetime.datetime(2000, 1, 1, 0, 0))

        rol1 = enrollments[1]
        self.assertIsInstance(rol0.organization, Organization)
        self.assertEqual(rol1.organization.name, 'Bitergia')
        self.assertEqual(rol1.start, datetime.datetime(2006, 1, 1, 0, 0))
        self.assertEqual(rol1.end, datetime.datetime(2008, 1, 1, 0, 0))

        rol2 = enrollments[2]
        self.assertIsInstance(rol0.organization, Organization)
        self.assertEqual(rol2.organization.name, 'Example')
        self.assertEqual(rol2.start, datetime.datetime(1900, 1, 1, 0, 0))
        self.assertEqual(rol2.end, datetime.datetime(2100, 1, 1, 0, 0))

    def test_valid_organizations_stream(self):
        """Check whether it parses organizations section from a valid stream"""

        stream = self.read_file('data/sortinghat_valid.json')

        parser = SortingHatParser(stream)
        orgs = parser.organizations

        # Check parsed organizations
        self.assertEqual(len(orgs), 3)

        # Bitergia entry
        org = orgs[0]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Bitergia')

        doms = org.domains
        self.assertEqual(len(doms), 4)

        dom = doms[0]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'api.bitergia.com')
        self.assertEqual(dom.is_top_domain, False)

        dom = doms[1]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'bitergia.com')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[2]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'bitergia.net')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[3]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'test.bitergia.com')
        self.assertEqual(dom.is_top_domain, False)

        # Example entry
        org = orgs[1]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Example')

        doms = org.domains
        self.assertEqual(len(doms), 2)

        dom = doms[0]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'example.com')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[1]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'example.net')
        self.assertEqual(dom.is_top_domain, True)

        # Unknown entry
        org = orgs[2]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Unknown')

        doms = org.domains
        self.assertEqual(len(doms), 0)

    def test_not_valid_stream(self):
        """Check whether it prints an error when parsing invalid streams"""

        with self.assertRaisesRegexp(InvalidFormatError,
                                     SH_INVALID_JSON_FORMAT_ERROR):
            s = self.read_file('data/sortinghat_invalid.json')
            SortingHatParser(s)

        with self.assertRaisesRegexp(InvalidFormatError,
                                     SH_IDS_MISSING_KEYS_ERROR):
            s = self.read_file('data/sortinghat_ids_missing_keys.json')
            SortingHatParser(s)

        with self.assertRaisesRegexp(InvalidFormatError,
                                     SH_ORGS_MISSING_KEYS_ERROR):
            s = self.read_file('data/sortinghat_orgs_missing_keys.json')
            SortingHatParser(s)

        with self.assertRaisesRegexp(InvalidFormatError,
                                     SH_IDS_DATETIME_ERROR):
            s = self.read_file('data/sortinghat_ids_invalid_date.json')
            SortingHatParser(s)

        with self.assertRaisesRegexp(InvalidFormatError,
                                     SH_ORGS_IS_TOP_ERROR):
            s = self.read_file('data/sortinghat_orgs_invalid_top.json')
            SortingHatParser(s)

    def test_empty_stream(self):
        """Check whether it raises an exception when the stream is empty"""

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_STREAM_INVALID_ERROR):
            SortingHatParser("")

    def test_none_stream(self):
        """Check whether it raises an exception when the stream is None"""

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_STREAM_INVALID_ERROR):
            SortingHatParser(None)


class TestSortingHatOrganizationsParser(TestBaseCase):
    """Test SortingHat parser with some inputs"""

    def test_valid_organizations_stream(self):
        """Check whether it parses a valid stream"""

        stream = self.read_file('data/sortinghat_orgs_valid.json')

        parser = SortingHatOrganizationsParser()
        orgs = [org for org in parser.organizations(stream)]

        # Check parsed organizations
        self.assertEqual(len(orgs), 3)

        # Unknown entry
        org = orgs[0]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Unknown')

        doms = org.domains
        self.assertEqual(len(doms), 0)

        # Bitergia entry
        org = orgs[1]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Bitergia')

        doms = org.domains
        self.assertEqual(len(doms), 4)

        dom = doms[0]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'api.bitergia.com')
        self.assertEqual(dom.is_top_domain, False)

        dom = doms[1]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'bitergia.com')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[2]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'bitergia.net')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[3]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'test.bitergia.com')
        self.assertEqual(dom.is_top_domain, False)

        # Example entry
        org = orgs[2]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.name, 'Example')

        doms = org.domains
        self.assertEqual(len(doms), 2)

        dom = doms[0]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'example.com')
        self.assertEqual(dom.is_top_domain, True)

        dom = doms[1]
        self.assertIsInstance(dom, Domain)
        self.assertEqual(dom.domain, 'example.net')
        self.assertEqual(dom.is_top_domain, True)

    def test_check(self):
        """Test check method"""

        parser = SortingHatOrganizationsParser()

        s = self.read_file('data/sortinghat_orgs_valid.json')
        result = parser.check(s)
        self.assertEqual(result, True)

        s = self.read_file('data/sortinghat_orgs_invalid_json.json')
        result = parser.check(s)
        self.assertEqual(result, False)

        s = self.read_file('data/sortinghat_orgs_missing_keys.json')
        result = parser.check(s)
        self.assertEqual(result, True)

        s = self.read_file('data/sortinghat_orgs_invalid_top.json')
        result = parser.check(s)
        self.assertEqual(result, True)

        s = "{'organizations' : null}"
        result = parser.check(s)
        self.assertEqual(result, False)

        s = "{'time' : null}"
        result = parser.check(s)
        self.assertEqual(result, False)

        result = parser.check("")
        self.assertEqual(result, False)

        result = parser.check(None)
        self.assertEqual(result, False)

    def test_not_valid_organizations_stream(self):
        """Check whether it prints an error when parsing invalid streams"""

        parser = SortingHatOrganizationsParser()

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_INVALID_JSON_FORMAT_ERROR):
            s1 = self.read_file('data/sortinghat_orgs_invalid_json.json')
            [org for org in parser.organizations(s1)]

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_MISSING_KEYS_ERROR):
            s2 = self.read_file('data/sortinghat_orgs_missing_keys.json')
            [org for org in parser.organizations(s2)]

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_IS_TOP_ERROR):
            s3 = self.read_file('data/sortinghat_orgs_invalid_top.json')
            [org for org in parser.organizations(s3)]

    def test_empty_organizations_stream(self):
        """Check whether it raises an exception when the stream is empty"""

        parser = SortingHatOrganizationsParser()

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_STREAM_INVALID_ERROR):
            [org for org in parser.organizations("")]

    def test_none_organizations_stream(self):
        """Check whether it raises an exception when the stream is None"""

        parser = SortingHatOrganizationsParser()

        with self.assertRaisesRegexp(InvalidFormatError,
                                     ORGS_STREAM_INVALID_ERROR):
            [org for org in parser.organizations(None)]


if __name__ == "__main__":
    unittest.main(buffer=True, exit=False)