"""
moai.server
===========

The Server module contains implementations
of :ref:`IServer` and :ref:`IFeedConfig`.

"""
from moai.oai import OAIServerFactory


class Server(object):
    """This is the default implementation of the
    :ref:`IServer` interface.

    """

    def __init__(self, base_url, db, config):
        self.base_url = base_url
        self._db = db
        self._config = config

    def handle_request(self, req):
        if not req.url().startswith(self.base_url):
            return req.send_status(
                '500 Internal Server Error',
                'The url "%s" does not start with base url "%s".' % (
                    req.url(), self.base_url))
        url = req.url()[len(self.base_url):]

        if url.startswith('/'):
            url = url[1:]
        if url.endswith('/'):
            url = url[:-1]

        urlparts = url.split('/')

        if len(urlparts) == 0:
            return req.send_status('500 Internal Server Error',
                                   'No server was selected, please append server name to url.')

        url = '/'.join(urlparts)

        oai_server = OAIServerFactory(self._db, self._config)
        return req.write(oai_server.handleRequest(req.query_dict()), 'text/xml')


class FeedConfig(object):
    """The feedconfig object contains all the settings for a specific
    feed. It implements the :ref:`IFeedConfig` interface.
    """

    def __init__(self,
                 repository_name,
                 base_url,
                 admin_emails=None,
                 metadata_prefixes=None,
                 batch_size=100,
                 content_type=None,
                 sets_needed=None,
                 sets_allowed=None,
                 sets_disallowed=None,
                 sets_deleted=None,
                 filter_sets=None,
                 extra_args=None):
        extra_args = extra_args or {}
        self.name = repository_name
        self.url = base_url
        self.admins = admin_emails or []
        self.metadata_prefixes = metadata_prefixes or ['oai_dc']
        self.batch_size = batch_size
        self.content_type = content_type
        self.sets_needed = set(sets_needed or [])
        self.sets_allowed = set(sets_allowed or [])
        self.sets_disallowed = set(sets_disallowed or [])
        self.sets_deleted = set(sets_deleted or [])
        self.filter_sets = set(filter_sets or [])
        self.delay = extra_args.get('delay', 0)
        self.oai_id_prefix = extra_args.get('oai_id_prefix', '')
