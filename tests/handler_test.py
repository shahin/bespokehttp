import os
import tempfile
import shutil
import unittest

from bespokehttp.handler import HttpRequestHandler

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


if __name__ == '__main__':
    unittest.main()
