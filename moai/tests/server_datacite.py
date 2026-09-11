import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerDataciteTest(ServerTest):

    def test_list_identifiers(self):
        response = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=datacite')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])

    def test_list_with_dates(self):
        response_from = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=datacite&from=2010-01-01')
        doc = etree.fromstring(response_from.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package3'])
        response_until = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=datacite&until=2010-01-01')
        doc = etree.fromstring(response_until.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2'])

    def test_list_records(self):
        response1 = requests.get('http://test?verb=ListRecords&metadataPrefix=datacite')
        doc = etree.fromstring(response1.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  "datacite": "http://datacite.org/schema/kernel-4"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])
        self.assertEqual(sorted(xpath.strings('//datacite:title')),
                         ['Test package 1', 'Test package 2', 'Test package 3'])
        self.assertIn("abc", xpath.strings('//datacite:subject'))
        self.assertIn("Natural Sciences - Biological sciences (1.6)", xpath.strings('//datacite:subject'))
        self.assertEqual(xpath.string('//datacite:description'), 'Just for testing')
        self.assertEqual(xpath.string('//datacite:identifier'), '10.00012/UU01-9SYIHN')
        self.assertEqual(xpath.string('//datacite:language'), 'en')
        self.assertEqual(xpath.string('//datacite:rights'), 'Creative Commons Attribution 4.0 International Public License')
        self.assertEqual(xpath.string('//datacite:creatorName'), 'A B')
        self.assertEqual(xpath.string('//datacite:affiliation'), 'Academic Center for Dentistry Amsterdam')
        self.assertEqual(xpath.string('//datacite:relatedIdentifier[@relationType="IsVersionOf"][@relatedIdentifierType="DOI"]'), '10.00012/UU01-AJPP6S')
