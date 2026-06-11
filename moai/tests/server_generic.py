import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerGenericTest(ServerTest):

    def test_identify(self):
        response = requests.get('http://test?verb=Identify')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.string('//oai:repositoryName'), 'Test Server')

    def test_list_sets(self):
        response = requests.get('http://test?verb=ListSets')
        # Sets have been disabled in the UU version of MOAI
        self.assertTrue('<error code="noSetHierarchy"></error>' in str(response.content))

    def test_list_metadata_formats(self):
        response = requests.get('http://test?verb=ListMetadataFormats')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(sorted(xpath.strings('//oai:metadataPrefix')),
                         ['datacite', 'iso19139', 'oai_dc'])

    def test_get_record(self):
        response = requests.get(
            'http://test?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:package1')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  'dc': 'http://purl.org/dc/elements/1.1/'})
        self.assertEqual(xpath.string('//oai:identifier'), 'oai:package1')
        self.assertEqual(xpath.string('//dc:title'), 'Test package 1')

    def test_get_record_unknown_identifier(self):
        response = requests.get(
            'http://test?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:unknownidentifier')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.string('//oai:error/@code'), 'idDoesNotExist')

    def test_bad_verb(self):
        response = requests.get('http://test?verb=NoSuchVerb')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.string('//oai:error/@code'), 'badVerb')

    def test_missing_metadata_prefix(self):
        response = requests.get('http://test?verb=ListRecords')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.string('//oai:error/@code'), 'badArgument')

    def test_unsupported_metadata_prefix(self):
        response = requests.get(
            'http://test?verb=ListRecords&metadataPrefix=formatdoesnotexist')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/"})
        self.assertEqual(xpath.string('//oai:error/@code'),
                         'cannotDisseminateFormat')
