import os
from unittest import TestCase

from moai.database import SQLDatabase
from moai.example import ExampleContent
from moai.provider.file import FileBasedContentProvider


class ProviderTest(TestCase):
    def setUp(self):
        path = os.path.abspath(os.path.dirname(__file__))
        self.provider = FileBasedContentProvider(
            'file://%s/../testdata/example*.xml' % path)
        self.db = SQLDatabase()

    def tearDown(self):
        del self.provider
        del self.db

    def test_provider_update(self):
        self.assertEqual(sorted([id for id in self.provider.update()]),
                         ['example-1234.xml', 'example-2345.xml'])

    def test_provider_content(self):
        self.assertEqual(sorted([id for id in self.provider.update()]),
                         ['example-1234.xml', 'example-2345.xml'])
        for content_id in self.provider.get_content_ids():
            raw_data = self.provider.get_content_by_id(content_id)
            content = ExampleContent(self.provider)
            content.update(raw_data)
            self.db.update_record(content.id,
                                  content.modified,
                                  content.deleted,
                                  content.sets,
                                  content.metadata)
        self.db.flush()
        self.assertEqual(self.db.record_count(), 2)
