import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerISO19139Test(ServerTest):

    def test_list_identifiers(self):
        response = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=iso19139')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])

    def test_list_with_dates(self):
        response_from = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=iso19139&from=2010-01-01')
        doc = etree.fromstring(response_from.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package3'])
        response_until = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=iso19139&until=2010-01-01')
        doc = etree.fromstring(response_until.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2'])

    def test_list_records(self):
        response1 = requests.get('http://test?verb=ListRecords&metadataPrefix=iso19139')
        doc = etree.fromstring(response1.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  "iso19139": "http://www.isotc211.org/2005/gmd",
                                  'gco': 'http://www.isotc211.org/2005/gco'})
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])
        self.assertEqual(sorted(xpath.strings('//iso19139:title/gco:CharacterString')),
                         ['Test package 1', 'Test package 2', 'Test package 3'])
        self.assertIn("abc", xpath.strings('//iso19139:keyword/gco:CharacterString'))
        self.assertIn("Natural Sciences - Biological sciences (1.6)", xpath.strings('//iso19139:keyword/gco:CharacterString'))
        self.assertEqual(xpath.string('//iso19139:abstract/gco:CharacterString'), 'Just for testing')
        self.assertEqual(xpath.string('//iso19139:fileIdentifier/gco:CharacterString'), 'doi:10.00012/UU01-9SYIHN')
        self.assertEqual(xpath.string('//iso19139:language/gco:CharacterString'), 'en')
        self.assertEqual(xpath.string('//iso19139:useLimitation/gco:CharacterString'), 'Creative Commons Attribution 4.0 International Public License')
        self.assertEqual(xpath.string('//iso19139:individualName/gco:CharacterString'), 'A B')
