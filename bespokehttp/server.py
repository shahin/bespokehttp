import os
import time
import mimetypes
import urllib
import errno

import SocketServer
from httprequest import HttpRequest, BadRequestError
from httpresponse import HttpResponse

class PermissionDeniedError(Exception):
    pass

class NonexistentResourceError(Exception):
    pass

class HttpServer(SocketServer.TCPServer):
    pass


class HttpRequestHandler(SocketServer.StreamRequestHandler):
    '''Parse a request, then construct and write a response.'''

    def handle(self):
        '''Read the request and write the response.'''

        self.data = self.rfile.readline().strip()
        self.request = HttpRequest(self.data)

        handler_method_name = 'respond_to_' + self.request.http_verb
        handler_method = getattr(self, handler_method_name, None)
        if not handler_method:
            raise NotImplementedError("Verb {} not supported.".format(self.request.http_verb))

        response = handler_method()
        response.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        self.wfile.write(response.render())
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
        '''Returns the contents of the given path.

        If the path refers to a directory, returns the directory listing of that path as a string.
        '''

        if os.path.isdir(path):
            return get_directory_list(path)

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

    def handle_error(self):
        pass


if __name__ == '__main__':

    HOST, PORT = 'localhost', 9191
    server = HttpServer((HOST, PORT, ), HttpRequestHandler)
    server.serve_forever()
