import os
import tempfile
import shutil
import unittest

from functools import wraps

from bespokehttp.handler import HttpRequestHandler, CgiRequestHandler


def with_temp_script(test_method):
    '''Creates an ephemeral temp file in a temp directory in the working directory.

    The file path is passed to the wrapped method as the second argument. The file and directory
    are deleted when the wrapped function returns.'''

    @wraps(test_method)
    def func_wrapper(self):
        with tempfile.TemporaryDirectory(dir='./') as dirname:
            with tempfile.NamedTemporaryFile(dir=dirname) as script_file:
                test_method(self, script_file.name)

    return func_wrapper

class HttpRequestHandlerTestCase(unittest.TestCase):

    def test_responds_200_to_request_for_file(self):
        tempdir = tempfile.mkdtemp(dir='./')

        with open(os.path.join(tempdir, 'resource.txt'), 'w') as resource_file:
            resource_file.write('resource content')

        request = 'GET {} HTTP/1.0\r\n\r\n'.format(resource_file.name[1:]).encode()
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertTrue(response.decode().startswith('HTTP/1.0 200 OK'))

        shutil.rmtree(tempdir)

    def test_responds_404_to_request_for_file(self):
        request = b'GET nonexistent HTTP/1.0\r\n\r\n'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertTrue(response.decode().startswith('HTTP/1.0 404 Not Found'))

    def test_responds_400_to_invalid_request(self):
        request = b'GET nonexistent\r\n\r\n'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertTrue(response.decode().startswith('HTTP/1.0 400 Bad Request'))

        request = b'PUT nonexistent HTTP/1.0\r\nContent-Length:5\r\n\r\nabcdef'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertTrue(response.decode().startswith('HTTP/1.0 400 Bad Request'))

    def test_empty_response_to_incomplete_request(self):
        request = b'GET nonexis'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertEqual(response, b'')

        request = b'GET nonexistent HTTP'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertEqual(response, b'')

        request = b'PUT nonexistent HTTP/1.0\r\nContent-Length:5\r\n\r\nabcd'
        handler = HttpRequestHandler(request)
        response = handler.handle()
        self.assertEqual(response, b'')

    @with_temp_script
    def test_parse_cgi_script_path(self, script_path):
        CgiRequestHandler.cgi_directory = os.path.split(os.path.abspath(script_path))[0]

        request_path = os.path.relpath(script_path, './')
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        actual_script_path, actual_path_info, actual_query, actual_fragment = \
                handler.parse_cgi_script_path(request_path)

        expected_script_path = script_path
        self.assertEqual(expected_script_path, actual_script_path)
        self.assertEqual('', actual_path_info)
        self.assertEqual('', actual_query)
        self.assertEqual('', actual_fragment)

        expected_path_info = 'hello/dog'
        request_path = os.path.join(os.path.relpath(script_path, './'), expected_path_info)
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        actual_script_path, actual_path_info, actual_query, actual_fragment = \
                handler.parse_cgi_script_path(request_path)

        expected_script_path = script_path
        self.assertEqual(expected_script_path, actual_script_path)
        self.assertEqual(expected_path_info, actual_path_info)
        self.assertEqual('', actual_query)
        self.assertEqual('', actual_fragment)

        expected_path_info = 'hello/dog'
        expected_query = 'abc=1&def=2'
        request_path = os.path.join(os.path.relpath(script_path, './'), expected_path_info) + '?' + expected_query
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        actual_script_path, actual_path_info, actual_query, actual_fragment = \
                handler.parse_cgi_script_path(request_path)

        expected_script_path = script_path
        self.assertEqual(expected_script_path, actual_script_path)
        self.assertEqual(expected_path_info, actual_path_info)
        self.assertEqual(expected_query, actual_query)
        self.assertEqual('', actual_fragment)

        expected_path_info = ''
        expected_query = 'abc=1&def=2'
        request_path = os.path.join(os.path.relpath(script_path, './'), expected_path_info) + '?' + expected_query
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        actual_script_path, actual_path_info, actual_query, actual_fragment = \
                handler.parse_cgi_script_path(request_path)

        expected_script_path = script_path
        self.assertEqual(expected_script_path, actual_script_path)
        self.assertEqual(expected_path_info, actual_path_info)
        self.assertEqual(expected_query, actual_query)
        self.assertEqual('', actual_fragment)

    def test_cgi_script_output(self):
        CgiRequestHandler.cgi_directory = os.path.abspath('tests')

        request_path = 'tests/cgi.py'
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        response = handler.handle()
        expected_response_body = b'PATH_INFO: \nQUERY_STRING: \n'
        self.assertTrue(response.endswith(expected_response_body))

        request_path = 'tests/cgi.py/hello/dog'
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        response = handler.handle()
        expected_response_body = b'PATH_INFO: hello/dog\nQUERY_STRING: \n'
        self.assertTrue(response.endswith(expected_response_body))

        request_path = 'tests/cgi.py/hello/dog?var1=1'
        request = 'GET {} HTTP/1.1\r\n\r\n'.format(request_path).encode()
        handler = CgiRequestHandler(request)
        response = handler.handle()
        expected_response_body = b'PATH_INFO: hello/dog\nQUERY_STRING: var1=1\n'
        self.assertTrue(response.endswith(expected_response_body))


if __name__ == '__main__':
    unittest.main()
