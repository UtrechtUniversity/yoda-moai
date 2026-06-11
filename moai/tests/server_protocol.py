import datetime
import urllib.parse

import requests
from lxml import etree

from moai.server import FeedConfig, Server
from moai.tests.server import ServerTest
from moai.utils import XPath
from moai.wsgi import MOAIWSGIApp

OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/"}


class ServerResumptionTest(ServerTest):
    """Test batched harvesting with resumption tokens.

    Real harvesters retrieve large repositories in batches, so the
    resumptionToken flow needs to work end to end.
    """

    def setUp(self):
        super().setUp()
        # replace the server with one that uses a batch size smaller
        # than the number of records, to force resumption tokens
        self.config = FeedConfig('Test Server',
                                 'http://test',
                                 admin_emails=['testuser@localhost'],
                                 metadata_prefixes=['oai_dc', 'datacite', 'iso19139'],
                                 batch_size=2)
        self.server = Server('http://test', self.db, self.config)
        self.app = MOAIWSGIApp(self.server)

    def harvest_identifiers(self, verb):
        # follow resumption tokens until the list is exhausted
        identifiers = []
        url = 'http://test?verb=%s&metadataPrefix=oai_dc' % verb
        for _ in range(10):
            response = requests.get(url)
            doc = etree.fromstring(response.content)
            xpath = XPath(doc, nsmap=OAI_NS)
            identifiers.extend(xpath.strings('//oai:identifier'))
            token = xpath.string('//oai:resumptionToken')
            if not token:
                break
            url = 'http://test?verb=%s&resumptionToken=%s' % (
                verb, urllib.parse.quote(token))
        return identifiers

    def test_list_identifiers_batches(self):
        response = requests.get(
            'http://test?verb=ListIdentifiers&metadataPrefix=oai_dc')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap=OAI_NS)
        # only the first batch is returned, plus a resumption token
        self.assertEqual(len(xpath.strings('//oai:identifier')), 2)
        self.assertTrue(xpath.string('//oai:resumptionToken'))

    def test_list_identifiers_full_harvest(self):
        self.assertEqual(sorted(self.harvest_identifiers('ListIdentifiers')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])

    def test_list_records_full_harvest(self):
        self.assertEqual(sorted(self.harvest_identifiers('ListRecords')),
                         ['oai:package1', 'oai:package2', 'oai:package3'])


class ServerDeletedRecordTest(ServerTest):
    """Test that deleted records are advertised with a deleted status,
    as required for the 'transient' deletedRecord support announced
    by the Identify verb.
    """

    def setUp(self):
        super().setUp()
        self.db.update_record('oai:gone',
                              datetime.datetime(2010, 12, 1, 12, 30, 00),
                              True, {}, {})
        self.db.flush()

    def test_list_identifiers_marks_deleted(self):
        response = requests.get(
            'http://test?verb=ListIdentifiers&metadataPrefix=oai_dc')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap=OAI_NS)
        self.assertEqual(sorted(xpath.strings('//oai:identifier')),
                         ['oai:gone', 'oai:package1',
                          'oai:package2', 'oai:package3'])
        deleted = xpath(
            '//oai:header[@status="deleted"]/oai:identifier/text()')
        self.assertEqual([str(i) for i in deleted], ['oai:gone'])

    def test_get_record_deleted(self):
        response = requests.get(
            'http://test?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:gone')
        doc = etree.fromstring(response.content)
        xpath = XPath(doc, nsmap=OAI_NS)
        self.assertEqual(xpath.string('//oai:header/@status'), 'deleted')
        # a deleted record must not contain a metadata part
        self.assertEqual(xpath('//oai:metadata'), [])
