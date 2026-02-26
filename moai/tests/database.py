import datetime
from unittest import TestCase

from moai.database import SQLDatabase


class DatabaseTest(TestCase):
    def setUp(self):
        self.db = SQLDatabase()

    def tearDown(self):
        del self.db

    def test_update(self):
        # db is empty
        self.assertEqual(self.db.record_count(), 0)
        # let's add a record
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False,
                              {},
                              {'title': 'Spam!'})
        self.db.flush()
        self.assertEqual(self.db.record_count(), 1)
        # check if all values are there
        record = self.db.get_record('oai:spam')
        self.assertEqual(record['id'], 'oai:spam')
        self.assertEqual(record['deleted'], False)
        self.assertEqual(record['modified'],
                         datetime.datetime(2010, 10, 13, 12, 30, 00))
        self.assertEqual(record['sets'], [])
        self.assertEqual(record['metadata'], {'title': 'Spam!'})
        # change a metadata value
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 10, 13, 12, 30, 0o1),
                              False,
                              {},
                              {'title': 'Ham!'})
        self.db.flush()
        self.assertEqual(self.db.record_count(), 1)
        # check if metadata was changed
        record = self.db.get_record('oai:spam')
        self.assertEqual(record['metadata'], {'title': 'Ham!'})
        # remove the record
        self.db.remove_record('oai:spam')
        self.assertEqual(self.db.record_count(), 0)

    def test_setrefs(self):
        # add a record that references a set
        self.assertEqual(self.db.set_count(), 0)
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False,
                              {'spamset': {'name': 'Spam Set',
                                           'description': 'spam spam spam',
                                           'hidden': False}},
                              {'title': 'Spam!'})
        self.db.flush()
        self.assertEqual(self.db.record_count(), 1)
        self.assertEqual(self.db.set_count(), 1)
        # check if all values are there
        record = self.db.get_record('oai:spam')
        self.assertEqual(record['sets'], ['spamset'])
        set = self.db.get_set('spamset')
        self.assertEqual(set['id'], 'spamset')
        self.assertEqual(set['name'], 'Spam Set')
        self.assertEqual(set['description'], 'spam spam spam')
        self.assertEqual(set['hidden'], False)
        # now, we'll change the record to use the hamset
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False,
                              {'hamset': {'name': 'Ham Set',
                                          'description': 'ham ham ham',
                                          'hidden': False}},
                              {'title': 'Ham!'})
        self.db.flush()
        self.assertEqual(self.db.record_count(), 1)
        # note that we now have 2 sets, the spam set is not removed
        self.assertEqual(self.db.set_count(), 2)
        # however, the spam record only has one reference
        record = self.db.get_record('oai:spam')
        self.assertEqual(record['sets'], ['hamset'])
        # if the set is removed then all references to that set are
        # also removed
        self.db.remove_set('hamset')
        record = self.db.get_record('oai:spam')
        self.assertEqual(record['sets'], [])
        self.assertEqual(self.db.set_count(), 1)

    def test_hidden_sets(self):
        # hidden sets are not added to the record setrefs list,
        # they are there though, for filtering purposes
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False,
                              {'spamset': {'name': 'Spam Set',
                                           'description': 'spam spam spam',
                                           'hidden': False},
                               'hamset': {'name': 'Ham Set',
                                          'description': 'ham ham ham',
                                          'hidden': True}},
                              {'title': 'Spam!'})
        self.db.flush()
        self.assertEqual(self.db.get_setrefs('oai:spam'), ['spamset'])
        self.assertEqual(self.db.get_setrefs('oai:spam',
                                             include_hidden_sets=True),
                         ['hamset', 'spamset'])
        # hidden sets are also never shown in the oai sets listing
        self.assertEqual(list(self.db.oai_sets()),
                         [{'description': 'spam spam spam',
                           'id': 'spamset',
                           'name': 'Spam Set'}])

    def test_earliest_datestamp(self):
        self.assertEqual(self.db.oai_earliest_datestamp(),
                         datetime.datetime(1970, 1, 1, 0, 0))
        self.db.update_record('oai:spam',
                              datetime.datetime(2009, 10, 13, 12, 30, 00),
                              False, {}, {})
        self.db.update_record('oai:ham',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False, {}, {})
        self.db.flush()
        self.assertEqual(self.db.oai_earliest_datestamp(),
                         datetime.datetime(2009, 10, 13, 12, 30))

    def test_oai_query_dates(self):
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 0o1, 0o1, 00, 00, 00),
                              False, {'spamset': {'name': 'spam'}},
                              {})
        self.db.update_record('oai:ham',
                              datetime.datetime(2009, 0o1, 0o1, 00, 00, 00),
                              False, {'hamset': {'name': 'ham'}},
                              {})
        self.db.flush()
        self.assertEqual(
            list(self.db.oai_query()),
            [{'deleted': False,
              'sets': ['spamset'],
              'metadata': {},
              'id': 'oai:spam',
              'modified': datetime.datetime(2010, 1, 1, 0, 0)},
             {'deleted': False,
              'sets': ['hamset'],
              'metadata': {},
              'id': 'oai:ham',
              'modified': datetime.datetime(2009, 1, 1, 0, 0)}])
        # date slices
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                from_date=datetime.datetime(2009, 6, 1, 0, 0))],
            ['oai:spam'])
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                until_date=datetime.datetime(2009, 6, 1, 0, 0))],
            ['oai:ham'])
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                from_date=datetime.datetime(2008, 6, 1, 0, 0),
                until_date=datetime.datetime(2010, 6, 1, 0, 0))],
            ['oai:spam', 'oai:ham'])
        # no matches
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                from_date=datetime.datetime(2011, 1, 1, 0, 0))],
            [])
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                until_date=datetime.datetime(2008, 1, 1, 0, 0))],
            [])
        # test inclusiveness
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(
                from_date=datetime.datetime(2009, 1, 1, 0, 0),
            )],
            ['oai:spam', 'oai:ham'])

    def test_oai_query_identifier(self):
        self.db.update_record('oai:spam',
                              datetime.datetime(2010, 0o1, 0o1, 00, 00, 00),
                              False, {'spamset': {'name': 'spam'}},
                              {})
        self.db.flush()
        self.assertEqual(
            [r['id'] for r in self.db.oai_query(identifier='oai:spam')],
            ['oai:spam'])

    def test_oai_query_future_dates(self):
        # records with a timestamp in the future should never
        # be returned, this feature can be used to create embargo dates
        self.db.update_record('oai:spam',
                              datetime.datetime(2040, 0o1, 0o1, 00, 00, 00),
                              False, {'spamset': {'name': 'spam'}},
                              {})
        self.db.flush()
        self.assertEqual(list(self.db.oai_query()), [])
        self.assertEqual(list(self.db.oai_query(
            until_date=datetime.datetime(2050, 0o1, 0o1, 00, 00, 00))), [])
        self.assertEqual(list(self.db.oai_query(identifier='oai:spam')), [])

    def test_oai_sets(self):
        self.db.update_record('oai:spam',
                              datetime.datetime(2009, 10, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset'),
                                      'test': dict(name='testset')}, {})
        self.db.update_record('oai:spamspamspam',
                              datetime.datetime(2009, 0o6, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset')}, {})
        self.db.update_record('oai:ham',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False, {'ham': dict(name='hamset'),
                                      'test': dict(name='testset')}, {})
        self.db.flush()
        # all records
        self.assertEqual([r['id'] for r in self.db.oai_query()],
                         ['oai:ham', 'oai:spam', 'oai:spamspamspam'])
        # only set ham
        self.assertEqual([r['id'] for r in self.db.oai_query(
            needed_sets=['ham'])], ['oai:ham'])
        # only set spam
        self.assertEqual([r['id'] for r in self.db.oai_query(
            needed_sets=['spam'])], ['oai:spam', 'oai:spamspamspam'])
        # records in spam set and test set
        self.assertEqual([r['id'] for r in self.db.oai_query(
            needed_sets=['test', 'spam'])], ['oai:spam'])
        # only allow records from certain sets
        self.assertEqual([r['id'] for r in self.db.oai_query(
            allowed_sets=['test'])], ['oai:ham', 'oai:spam'])
        self.assertEqual([r['id'] for r in self.db.oai_query(
            allowed_sets=['spam', 'ham'])],
            ['oai:ham', 'oai:spam', 'oai:spamspamspam'])
        # only allow records from certain sets, combined with set
        self.assertEqual([r['id'] for r in self.db.oai_query(
            allowed_sets=['test'], needed_sets=['spam'])],
            ['oai:spam'])
        self.assertEqual([r['id'] for r in self.db.oai_query(
            allowed_sets=['spam'], needed_sets=['test'])],
            ['oai:spam'])
        # certain records should always be disallowed
        self.assertEqual([r['id'] for r in self.db.oai_query(
            disallowed_sets=['spam'])],
            ['oai:ham'])
        # disallowed sets has precedence over allowed sets
        self.assertEqual([r['id'] for r in self.db.oai_query(
            disallowed_sets=['test'], allowed_sets=['spam'])],
            ['oai:spamspamspam'])

    def test_oai_batching(self):
        self.db.update_record('oai:spam',
                              datetime.datetime(2009, 10, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset'),
                                      'test': dict(name='testset')}, {})
        self.db.update_record('oai:spamspamspam',
                              datetime.datetime(2009, 0o6, 13, 12, 30, 00),
                              False, {'spam': dict(name='spamset')}, {})
        self.db.update_record('oai:ham',
                              datetime.datetime(2010, 10, 13, 12, 30, 00),
                              False, {'ham': dict(name='hamset'),
                                      'test': dict(name='testset')}, {})
        self.db.flush()
        self.assertEqual(len(list(self.db.oai_query())), 3)
        self.assertEqual(len(list(self.db.oai_query(batch_size=1))), 1)
        self.assertEqual([r['id'] for r in self.db.oai_query(
            batch_size=1)], ['oai:ham'])
        self.assertEqual([r['id'] for r in self.db.oai_query(
            batch_size=1, offset=1)], ['oai:spam'])
        self.assertEqual([r['id'] for r in self.db.oai_query(
            batch_size=1, offset=2)], ['oai:spamspamspam'])
