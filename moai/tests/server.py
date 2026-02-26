import datetime
import json
import os
from unittest import TestCase

from wsgi_intercept import add_wsgi_intercept, requests_intercept

from moai.database import SQLDatabase
from moai.server import FeedConfig, Server
from moai.wsgi import MOAIWSGIApp


class ServerTest(TestCase):
    def setUp(self):
        self.db = SQLDatabase()
        self.db.update_record('oai:package1',
                              datetime.datetime(2009, 10, 13, 12, 30, 00),
                              False, {'odd': dict(name='oddset')},
                              self.get_test_metadata("Test package 1"))
        self.db.update_record('oai:package2',
                              datetime.datetime(2009, 0o6, 13, 12, 30, 00),
                              False, {'prime': dict(name='primeset'),
                                      'even': dict(name='evenset')},
                              self.get_test_metadata("Test package 2"))
        self.db.update_record('oai:package3',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False, {'odd': dict(name='oddset'),
                                      'prime': dict(name='primeset')},
                              self.get_test_metadata("Test package 3"))
        self.db.flush()
        self.config = FeedConfig('Test Server',
                                 'http://test',
                                 admin_emails=['testuser@localhost'],
                                 metadata_prefixes=['oai_dc', 'datacite', 'iso19139'])
        self.server = Server('http://test', self.db, self.config)
        self.app = MOAIWSGIApp(self.server)
        requests_intercept.install()
        add_wsgi_intercept('test', 80, lambda: self.app)

    def tearDown(self):
        requests_intercept.uninstall()
        del self.app
        del self.server
        del self.db
        del self.config

    def get_test_metadata(self, title):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../testdata/yoda/yoda-test.json")
        with open(path, "r") as file:
            data = json.load(file)
            data["Title"] = title
        return data
