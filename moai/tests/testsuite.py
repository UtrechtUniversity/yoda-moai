from unittest import makeSuite, TestSuite

from moai.tests.database import DatabaseTest
from moai.tests.provider import ProviderTest
from moai.tests.server_datacite import ServerDataciteTest
from moai.tests.server_generic import ServerGenericTest
from moai.tests.server_iso19139 import ServerISO19139Test
from moai.tests.server_oaidc import ServerOAIDCTest
from moai.tests.server_protocol import ServerDeletedRecordTest, ServerResumptionTest
from moai.tests.xpath import XPathUtilTest
from moai.tests.yoda import YodaContentTest


def suite():
    test_suite = TestSuite()
    test_suite.addTest(makeSuite(XPathUtilTest))
    test_suite.addTest(makeSuite(DatabaseTest))
    test_suite.addTest(makeSuite(ProviderTest))
    test_suite.addTest(makeSuite(YodaContentTest))
    test_suite.addTest(makeSuite(ServerGenericTest))
    test_suite.addTest(makeSuite(ServerDataciteTest))
    test_suite.addTest(makeSuite(ServerISO19139Test))
    test_suite.addTest(makeSuite(ServerOAIDCTest))
    test_suite.addTest(makeSuite(ServerResumptionTest))
    test_suite.addTest(makeSuite(ServerDeletedRecordTest))
    # note that the core tests of the oai protocol itself are done in the
    # pyoai codebase
    return test_suite
