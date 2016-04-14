import unittest

from bespokehttp.httprequest import HttpRequest, BadRequestError

class HttpRequestTestCase(unittest.TestCase):

    def test_parse_request_line(self):
        request_line = 'GET /abc/def.html HTTP/1.1'
        expected = ('GET', '/abc/def.html', 'HTTP/1.1')
        actual = HttpRequest.parse_request_line(request_line)
        self.assertEqual(expected, actual)

        request_line = 'invalid request'
        with self.assertRaises(BadRequestError):
            actual = HttpRequest.parse_request_line(request_line)

    def test_parse_header_liens(self):
        header_lines = [
            'Accept: text/plain',
            'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
        ]
        expected = {
            'Accept': 'text/plain',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
        }
        actual = HttpRequest.parse_header_lines(header_lines)
        self.assertEqual(expected, actual)

        expected = {}
        actual = HttpRequest.parse_header_lines([])
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
