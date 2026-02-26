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
