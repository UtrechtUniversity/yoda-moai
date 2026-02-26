import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerOAIDCTest(ServerTest):

    def test_list_identifiers(self):
        response = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.strings('//oai:identifier'),
                         ['oai:ham', 'oai:spam', 'oai:spamspamspam'])

    def test_list_with_dates(self):
        response_from = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc&from=2010-01-01')
        doc = etree.fromstring(response_from.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.strings('//oai:identifier'),
                         ['oai:ham'])
        response_until = requests.get('http://test?verb=ListIdentifiers&metadataPrefix=oai_dc&until=2010-01-01')
        doc = etree.fromstring(response_until.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.strings('//oai:identifier'),
                         ['oai:spam', 'oai:spamspamspam'])

    def test_list_records(self):
        response1 = requests.get('http://test?verb=ListRecords&metadataPrefix=oai_dc')
        doc = etree.fromstring(response1.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  "dc": "http://purl.org/dc/elements/1.1/"})
        self.assertEqual(xpath.strings('//oai:identifier'),
                         ['oai:ham', 'oai:spam', 'oai:spamspamspam'])
        self.assertEqual(xpath.strings('//dc:title'),
                         ['Ham!', 'Spam!', 'Spam Spam Spam!'])
