import unittest

from bespokehttp.httprequest import (
    HttpRequest,
    InvalidRequestError,
    IncompleteRequestError,
    MissingContentLengthError
)

class HttpRequestTestCase(unittest.TestCase):

    def test_parse_request_line(self):
        request_line = b'GET /abc/def.html HTTP/1.0'
        expected = ('GET', '/abc/def.html', 'HTTP/1.0')
        actual = HttpRequest.parse_request_line(request_line)
        self.assertEqual(expected, actual)

        request_line = b'invalid request'
        with self.assertRaises(InvalidRequestError):
            actual = HttpRequest.parse_request_line(request_line)

    def test_parse_header_liens(self):
        header_lines = [
            b'Accept: text/plain',
            b'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
        ]
        expected = {
            b'Accept': b'text/plain',
            b'User-Agent': b'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
        }
        actual = HttpRequest.parse_header_lines(header_lines)
        self.assertEqual(expected, actual)

        expected = {}
        actual = HttpRequest.parse_header_lines([])
        self.assertEqual(expected, actual)

    def test_parse_get_requests(self):
        request_message = b'GET /abc/def.html HTTP/1.0\r\n\r\n'
        request = HttpRequest(request_message)
        self.assertEqual(request.http_verb, 'GET')
        self.assertEqual(request.version, 'HTTP/1.0')
        self.assertEqual(request.path, '/abc/def.html')
        self.assertEqual(request.headers, {})
        self.assertEqual(request.content_length, 0)
        self.assertEqual(request.body, b'')

        request_message = b'GET /abc/def.html HTTP/1.0\r\nContent-Type: text/plain\r\n\r\n'
        request = HttpRequest(request_message)
        self.assertEqual(request.http_verb, 'GET')
        self.assertEqual(request.version, 'HTTP/1.0')
        self.assertEqual(request.path, '/abc/def.html')
        self.assertEqual(request.headers, {b'Content-Type': b'text/plain'})
        self.assertEqual(request.content_length, 0)
        self.assertEqual(request.body, b'')

    def test_parse_post_requests(self):
        request_message = b'POST /abc/def.html HTTP/1.0\r\nContent-Length: 0\r\n\r\n'
        request = HttpRequest(request_message)
        self.assertEqual(request.http_verb, 'POST')
        self.assertEqual(request.version, 'HTTP/1.0')
        self.assertEqual(request.path, '/abc/def.html')
        self.assertEqual(request.headers, {b'Content-Length': b'0'})
        self.assertEqual(request.content_length, 0)
        self.assertEqual(request.body, b'')

        request_message = b'POST /abc/def.html HTTP/1.0\r\nContent-Length: 2\r\n\r\nab'
        request = HttpRequest(request_message)
        self.assertEqual(request.http_verb, 'POST')
        self.assertEqual(request.version, 'HTTP/1.0')
        self.assertEqual(request.path, '/abc/def.html')
        self.assertEqual(request.headers, {b'Content-Length': b'2'})
        self.assertEqual(request.content_length, 2)
        self.assertEqual(request.body, b'ab')

    def test_incomplete_requests_cause_exception(self):
        request = b'G'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html H'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\n'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Len'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Length:0'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Length:0\r\n'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Length:0\r\n\r'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Length:0\r\n\n'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\nContent-Length:1\r\n\r\n'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'POST /abc/def.html HTTP/1.0\r\nContent-Length:1\r\n\r\n'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

        request = b'POST /abc/def.html HTTP/1.0\r\nContent-Length:2\r\n\r\na'
        with self.assertRaises(IncompleteRequestError):
            HttpRequest(request)

    def test_invalid_requests_cause_exception(self):
        request = b'G\r\n\r\n'
        with self.assertRaises(InvalidRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html\r\n\r\n'
        with self.assertRaises(InvalidRequestError):
            HttpRequest(request)

        request = b'GET /abc/def.html HTTP/1.0\r\n\Content-Length\r\n\r\n'
        with self.assertRaises(InvalidRequestError):
            HttpRequest(request)

        request = b'POST /abc/def.html HTTP/1.0\r\nContent-Length:2\r\n\r\nabc'
        with self.assertRaises(InvalidRequestError):
            HttpRequest(request)

    def test_post_request_requires_content_length(self):
        request = b'POST /abc/def.html HTTP/1.0\r\n\r\na'
        with self.assertRaises(MissingContentLengthError):
            HttpRequest(request)

if __name__ == '__main__':
    unittest.main()
