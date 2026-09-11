import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerOAIDCTest(ServerTest):

    def test_list_identifiers(self):
        response = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])

    def test_list_with_dates(self):
        response_from = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc&from=2010-01-01')
        doc = etree.fromstring(response_from.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package3'])
        response_until = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc&until=2010-01-01')
        doc = etree.fromstring(response_until.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2'])

    def test_list_records(self):
        response1 = requests.get('http://test?verb=ListRecords&metadataPrefix=oai_dc')
        doc = etree.fromstring(response1.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                                  'dc': 'http://purl.org/dc/elements/1.1/'})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])
        self.assertEqual(sorted(xpath.strings('//dc:title')),
                         ['Test package 1', 'Test package 2', 'Test package 3'])
        self.assertIn("abc", xpath.strings('//dc:subject'))
        self.assertIn("Natural Sciences - Biological sciences (1.6)", xpath.strings('//dc:subject'))
        self.assertEqual(xpath.string('//dc:description'), 'Just for testing')
        self.assertEqual(set(xpath.strings('//dc:identifier')), {'doi:10.00012/UU01-9SYIHN', 'doi:10.00012/UU01-AJPP6S'})
        self.assertEqual(xpath.string('//dc:language'), 'en - English')
        self.assertEqual(xpath.string('//dc:rights'), 'Creative Commons Attribution 4.0 International Public License (https://creativecommons.org/licenses/by/4.0/legalcode) | Open Access (info:eu-repo/semantics/openAccess)')
        self.assertEqual(xpath.string('//dc:creator'), 'A B (Academic Center for Dentistry Amsterdam)')
