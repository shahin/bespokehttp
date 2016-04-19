import os
import time
import mimetypes
import urllib
import errno
import io

import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

from bespokehttp.httprequest import HttpRequest, IncompleteRequestError, InvalidRequestError
from bespokehttp.httpresponse import HttpResponse


class PermissionDeniedError(Exception):
    pass

class NonexistentResourceError(Exception):
    pass


class HttpRequestHandler(object):
    '''Parse a request, then construct and write a response.'''

    def __init__(self, data):
        self.data = io.BytesIO(data)

    def handle(self):
        '''Read the request and write the response.'''

        LOG.info('Reading request: {}'.format(self.data.getvalue()))

        try:
            self.request = HttpRequest(self.data.getvalue())
        except IncompleteRequestError:
            # keep collecting data from the connection
            return b'' 
        except InvalidRequestError:
            # send a response that says what it got is invalid, no matter what comes next
            # e.g. a CR or LF before the end of the first line
            response = HttpResponse(400)
        else:
            handler_method_name = 'respond_to_' + self.request.http_verb.decode()
            handler_method = getattr(self, handler_method_name, None)
            if handler_method:
                response = handler_method()
            else:
                response = HttpResponse(405)

        response.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        LOG.info('Sending response: {}'.format(response.lines[0]))
        return response.render()

    def respond_to_GET(self):
        '''Returns an HttpResponse to a GET request.'''

        resource_path, _, _ = self.get_resource_path(self.request.path)

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
        except IOError as e:
            if e.errno == errno.EACCES:
                raise PermissionDeniedError()
            elif e.errno == errno.ENOENT:
                raise NonexistentResourceError()
            else:
                raise e

        type, encoding = mimetypes.guess_type(path)
        return type, encoding, contents

    @staticmethod
    def get_resource_path(path):
        '''Returns a 3-tuple of the absolute path, query string, and URL fragment of the resource
        requested by the request URL.'''
        path = path.decode()
        path, _, fragment = path.partition('#')
        path, _, query = path.partition('?')
        path = path[1:]

        path = os.path.abspath(urllib.parse.unquote(path))

        if os.path.isdir(path):
            for index_file_name in ('index.html', 'index.htm', ):
                index_path = os.path.join(path, index_file_name)
                if os.path.exists(index_path):
                    path = index_path

        return path, query, fragment 
