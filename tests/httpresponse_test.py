import unittest

from bespokehttp.httpresponse import HttpResponse

class HttpResponseTestCase(unittest.TestCase):

    def test_default_headers_contain_content_length(self):
        response = HttpResponse(200, 'ABCDEFG')
        self.assertEqual(response.headers['Content-Length'], '7')

        # include Content-Length even if content is reset to None, for e.g. HEAD responses
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.13
        response.content = None
        self.assertEqual(response.headers['Content-Length'], '7')

    def test_default_headers_can_be_overridden(self):
        response = HttpResponse(200, 'ABCD')
        self.assertEqual(response.headers['Server'], 'bespokehttp')
        response.headers['Server'] = 'notnginx'
        self.assertEqual(response.headers['Server'], 'notnginx')

        response = HttpResponse(200, 'ABCD', {'Server': 'notapache'})
        self.assertEqual(response.headers['Server'], 'notapache')

if __name__ == '__main__':
    unittest.main()
