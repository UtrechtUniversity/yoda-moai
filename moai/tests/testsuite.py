from unittest import makeSuite, TestSuite

from moai.tests.database import DatabaseTest
from moai.tests.provider import ProviderTest
from moai.tests.server_didl import ServerDIDLTest
from moai.tests.server_generic import ServerGenericTest
from moai.tests.server_oaidc import ServerOAIDCTest
from moai.tests.xpath import XPathUtilTest


def suite():
    test_suite = TestSuite()
    test_suite.addTest(makeSuite(XPathUtilTest))
    test_suite.addTest(makeSuite(DatabaseTest))
    test_suite.addTest(makeSuite(ProviderTest))
    test_suite.addTest(makeSuite(ServerGenericTest))
    test_suite.addTest(makeSuite(ServerDIDLTest))
    test_suite.addTest(makeSuite(ServerOAIDCTest))
    # note that tests of the oai protocol itself are done in the
    # pyoai codebase
    return test_suite
