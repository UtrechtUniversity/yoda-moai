import os
import tempfile
from datetime import datetime
from unittest import TestCase

from moai.yoda import YodaContent


class YodaContentTest(TestCase):
    """Tests for the Yoda specific content class that converts
    yoda-metadata.json files into MOAI records.
    """

    def setUp(self):
        self.content = YodaContent(None)
        self.testdata_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../testdata/yoda/yoda-test.json")

    def test_update_with_valid_metadata(self):
        result = self.content.update(self.testdata_path)
        self.assertNotEqual(result, False)
        # the OAI identifier is derived from the datapackage DOI
        self.assertEqual(self.content.id, 'oai:10.00012/UU01-9SYIHN')
        self.assertEqual(self.content.metadata['identifier'],
                         ['10.00012/UU01-9SYIHN'])
        # the full JSON document is stored under the 'metadata' key
        self.assertEqual(
            self.content.metadata['metadata']['Title'],
            'Test data package')
        self.assertEqual(self.content.deleted, False)
        # modified is backdated so the record is immediately harvestable
        self.assertIsInstance(self.content.modified, datetime)
        self.assertTrue(self.content.modified < datetime.now())

    def test_update_with_missing_file(self):
        result = self.content.update('/nonexistent/yoda-metadata.json')
        self.assertEqual(result, False)
        # nothing should be set on a failed update
        self.assertEqual(self.content.id, None)
        self.assertEqual(self.content.metadata, {})

    def test_update_with_invalid_json(self):
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False) as invalid_file:
            invalid_file.write('{"Title": "broken"')
            path = invalid_file.name
        try:
            result = self.content.update(path)
            self.assertEqual(result, False)
            self.assertEqual(self.content.id, None)
        finally:
            os.unlink(path)
