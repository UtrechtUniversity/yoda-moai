import datetime
from unittest import TestCase

from wsgi_intercept import add_wsgi_intercept, requests_intercept

from moai.database import SQLDatabase
from moai.server import FeedConfig, Server
from moai.wsgi import MOAIWSGIApp


class ServerTest(TestCase):
    def setUp(self):
        self.db = SQLDatabase()
        self.db.update_record('oai:spam',
                              datetime.datetime(2009, 10, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset'),
                                      'test': dict(name='testset')},
                              {'title': ['Spam!']})
        self.db.update_record('oai:spamspamspam',
                              datetime.datetime(2009, 0o6, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset')},
                              {'title': ['Spam Spam Spam!']})
        self.db.update_record('oai:ham',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False, {'ham': dict(name='hamset'),
                                      'test': dict(name='testset')},
                              {'title': ['Ham!']})
        self.db.flush()
        self.config = FeedConfig('Test Server',
                                 'http://test',
                                 admin_emails=['testuser@localhost'],
                                 metadata_prefixes=['oai_dc', 'mods', 'didl'])
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
