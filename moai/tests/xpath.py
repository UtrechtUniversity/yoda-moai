import datetime
from unittest import TestCase

from lxml import etree

from moai.utils import XPath


class XPathUtilTest(TestCase):

    def test_string(self):
        doc = etree.fromstring(
            '''<doc>
                 <string>test</string>
                 <string/>
                 <string>   test     </string>
                 <string>test<foo/>more test</string>
                 <string>tëst</string>
               </doc>''')
        xpath = XPath(doc)
        self.assertEqual(xpath.strings('/doc/string'),
                         ['test', 'test', 'test', 'tëst'])

    def test_boolean(self):
        doc = etree.fromstring(
            '''<doc>
                 <bool>yes</bool>
                 <bool>true</bool>
                 <bool>False</bool>
                 <bool>NO</bool>
               </doc>''')
        xpath = XPath(doc)
        self.assertEqual(xpath.booleans('/doc/bool'),
                         [True, True, False, False])

    def test_number(self):
        doc = etree.fromstring(
            '''<doc>
                 <number>1</number>
                 <number>3.33333333333</number>
                 <number>-75</number>
                 <number>-0.75</number>
               </doc>''')
        xpath = XPath(doc)
        numbers = xpath.numbers('/doc/number')
        self.assertEqual(numbers,
                         [1, 3.33333333333, -75, -0.75])
        self.assertEqual([type(i) for i in numbers],
                         [int, float, int, float])

    def test_date(self):
        doc = etree.fromstring(
            '''<doc>
                 <date>2010-01-04</date>
                 <date>2010/01/04</date>
                 <date>2010-01-04T12:43:33Z</date>
                 <date>2010-01-04T12:43:33</date>
               </doc>''')
        xpath = XPath(doc)
        self.assertEqual(xpath.dates('/doc/date'),
                         [datetime.datetime(2010, 1, 4, 0, 0),
                          datetime.datetime(2010, 1, 4, 0, 0),
                          datetime.datetime(2010, 1, 4, 12, 43, 33),
                          datetime.datetime(2010, 1, 4, 12, 43, 33)])

    def test_tags(self):
        doc = etree.fromstring('<doc><a/><b/><s:c xmlns:s="urn:spam"/></doc>')
        xpath = XPath(doc)
        self.assertEqual(xpath.tags('/doc/*'), ['a', 'b', 'c'])

    def test_namespaces(self):
        doc = etree.fromstring(
            '<doc xmlns="urn:spam"><string>Spam!</string></doc>')
        xpath = XPath(doc, nsmap={'spam': 'urn:spam'})
        self.assertEqual(xpath.string('//spam:string'), 'Spam!')
