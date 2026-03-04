from webob import Request, Response

from moai.database import get_database
from moai.server import FeedConfig, Server


class WSGIRequest(object):
    """This is a request object that can be used in a WSGI environment.
    It implements :ref:`IServerRequest` interface.
    """

    def __init__(self, request):
        self._req = request

    def url(self):
        return self._req.url

    def redirect(self, url):
        """Redirect to this url
        """
        response = Response()
        response.status = 302
        response.location = url
        return response

    def query_dict(self):
        """Return a dictionary with QueryString values of the
        request
        """
        args = dict(self._req.GET)
        args.update(dict(self._req.POST))
        return args

    def write(self, data, mimetype):
        """Write data back to the client
        """
        response = Response()
        response.content_type = mimetype
        response.body = data
        return response

    def send_status(self, code, msg='', mimetype='text/plain'):
        response = Response()
        response.content_type = mimetype
        response.status = int(code.split()[0])
        response.text = msg
        return response


class MOAIWSGIApp(object):
    # the wsgi app, calls the IServer with the IServerRequest
    def __init__(self, server):
        self.server = server

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.server.handle_request(WSGIRequest(request))
        return response(environ, start_response)


def app_factory(global_config,
                name,
                url,
                admin_email,
                database,
                formats,
                **kwargs):
    # WSGI APP Factory
    formats = formats.split()
    admin_email = admin_email.split()
    sets_deleted = kwargs.get('deleted_sets') or []
    if sets_deleted:
        sets_deleted = sets_deleted.split()
    sets_disallowed = kwargs.get('disallowed_sets', '') or []
    if sets_disallowed:
        sets_disallowed = sets_disallowed.split()
    sets_allowed = kwargs.get('allowed_sets', '') or []
    if sets_allowed:
        sets_allowed = sets_allowed.split()
    sets_needed = kwargs.get('needed_sets', '') or []
    if sets_needed:
        sets_needed = sets_needed.split()
    database = get_database(database, kwargs)
    feedconfig = FeedConfig(name,
                            url,
                            admin_emails=admin_email,
                            metadata_prefixes=formats,
                            sets_deleted=sets_deleted,
                            sets_disallowed=sets_disallowed,
                            sets_allowed=sets_allowed,
                            sets_needed=sets_needed,
                            extra_args=kwargs)
    server = Server(url, database, feedconfig)

    return MOAIWSGIApp(server)
