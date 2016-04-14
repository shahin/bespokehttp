import os
import time
import mimetypes
import urllib
import errno

from StringIO import StringIO

import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

from httprequest import HttpRequest, BadRequestError
from httpresponse import HttpResponse


class PermissionDeniedError(Exception):
    pass

class NonexistentResourceError(Exception):
    pass


class HttpRequestHandler(object):
    '''Parse a request, then construct and write a response.'''

    def __init__(self, request_data):
        self.rfile, self.wfile = StringIO(), StringIO()
        self.rfile.write(request_data)
        self.rfile.flush()
        self.rfile.seek(0)

    def handle(self):
        '''Read the request and write the response.'''

        self.data = self.rfile.read()
        self.request = HttpRequest(self.data)
        LOG.info('Received request: {}'.format(self.request.request_line))

        handler_method_name = 'respond_to_' + self.request.http_verb
        handler_method = getattr(self, handler_method_name, None)
        if not handler_method:
            raise NotImplementedError("HTTP verb {} not supported.".format(self.request.http_verb))

        response = handler_method()
        response.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        self.wfile.write(response.render())
        LOG.info('Sent response: {}'.format(response.lines[0]))
        self.wfile.flush()

    def respond_to_GET(self):
        '''Returns an HttpResponse to a GET request.'''

        resource_path, _, _ = self.get_resource_path(self.request.path)

        if not self.authorized(resource_path):
            return HttpResponse(403, None)

        try:
            type, encoding, content = self.read_resource(resource_path)
            response = HttpResponse(200, content)
        except PermissionDeniedError:
            response = HttpResponse(403, None)
        except NonexistentResourceError:
            response = HttpResponse(404, None)

        return response

    def respond_to_HEAD(self):
        '''Returns an HttpResponse to a HEAD request.'''
        response = self.respond_to_get()
        response.content = None
        return response 

    @staticmethod
    def read_resource(path):
        '''Returns the contents of file at the given path.
        
        If the path does not point to a file, raise a NonexistentResourceError. If the file exists
        but this user doesn't have permission, raise a PermissionDeniedError.'''

        if os.path.isdir(path):
            return NonexistentResourceError()

        contents = None

        try:
            f = open(path, 'rb')
            contents = f.read()
        except IOError, e:
            if e.errno == errno.EACCES:
                raise PermissionDeniedError()
            elif e.errno == errno.ENOENT:
                raise NonexistentResourceError()
            else:
                raise e

        type, encoding = mimetypes.guess_type(path)
        return type, encoding, contents

    def authorized(self, path):
        '''Returns True if the request passes handler-level authorization tests.'''
        serving_base_path = os.getcwd()
        if not path.startswith(serving_base_path):
            return False
        return True

    @staticmethod
    def get_resource_path(path):
        '''Returns a 3-tuple of the absolute path, query string, and URL fragment of the resource
        requested by the request URL.'''
        path, _, fragment = path.partition('#')
        path, _, query = path.partition('?')
        path = path[1:]

        path = os.path.abspath(urllib.unquote(path))

        if os.path.isdir(path):
            for index_file_name in ('index.html', 'index.htm', ):
                index_path = os.path.join(path, index_file_name)
                if os.path.exists(index_path):
                    path = index_path

        return path, query, fragment 
