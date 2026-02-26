import requests
from lxml import etree

from moai.tests.server import ServerTest
from moai.utils import XPath


class ServerDIDLTest(ServerTest):

    def test_list_records(self):
        response1 = requests.get('http://test?verb=ListRecords&metadataPrefix=didl')
        doc = etree.fromstring(response1.content)
        xpath = XPath(doc, nsmap={"oai": "http://www.openarchives.org/OAI/2.0/",
                                  "mods": "http://www.loc.gov/mods/v3"})
        self.assertEqual(xpath.strings('//mods:titleInfo/mods:title'),
                         ['Ham!', 'Spam!', 'Spam Spam Spam!'])
