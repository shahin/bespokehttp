import sys
import inspect

class HttpResponse(object):

    def __init__(self, status_code, content=None, headers=None):
        """Create an HTTP response that can be rendered to the client.

        Args:
            status_code (integer): the HTTP status code of the response
            content (bytes, optional): the message body; defaults to an empty string
            headers (dictionary, optional): header values, keyed by HTTP response header names;
                defaults to the default_headers property
        """
        self.status_code = status_code
        self.content = content or ''
        self.headers = self.default_headers.copy()
        if headers:
            self.headers.update(headers)

    @property
    def status_description(self):
        return self.statuses.get(self.status_code, '')

    @property
    def default_headers(self):
        content_length = len(self.content)
        default_headers = {
            'Connection': 'close',
            'Server': __name__.split('.')[0]
        }

        if content_length:
            default_headers['Content-Length'] = str(content_length)
        return default_headers

    @property
    def lines(self):
        _lines = []

        status_line = ['HTTP/1.0', str(self.status_code), self.status_description]
        _lines.append(' '.join(status_line))

        for header in self.headers.items():
            _lines.append(': '.join(header))

        _lines.append('')

        if self.content:
            _lines.append(self.content)

        return _lines

    def render(self):
        '''Return the full HTTP response message.'''
        return '\r\n'.join(self.lines)


    statuses = {
        200: 'OK',
        403: 'Forbidden',
        404: 'Not Found',
    }
