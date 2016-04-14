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

        request = 'GET {} HTTP/1.0'.format(resource_file.name[1:])
        handler = HttpRequestHandler(request)
        handler.handle()
        handler.wfile.seek(0)
        self.assertTrue(handler.wfile.read().startswith('HTTP/1.0 200 OK'))

        shutil.rmtree(tempdir)

    def test_responds_404_to_request_for_file(self):
        request = 'GET {} HTTP/1.0'.format('nonexistent')
        handler = HttpRequestHandler(request)
        handler.handle()
        handler.wfile.seek(0)
        self.assertTrue(handler.wfile.read().startswith('HTTP/1.0 404 Not Found'))

if __name__ == '__main__':
    unittest.main()
