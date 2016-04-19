import io

class InvalidRequestError(Exception):
    '''Raised when the request is syntactically invalid no matter what data we receive next.'''
    pass

class IncompleteRequestError(Exception):
    '''Raised when the request is semantically incomplete but may be completed given additional data.
    '''
    pass

class MissingContentLengthError(Exception):
    pass

class HttpRequest(object):

    http_version = '1.0'

    def __init__(self, request_data):
        self.data = request_data
        self.parse_request()

    def parse_request(self): 
        self.request_line, self.header_lines, self.body = self.extract_request_components(self.data)

        self.http_verb, self.path, self.version = self.parse_request_line(self.request_line)
        self.headers = self.parse_header_lines(self.header_lines)

        self.content_length = 0
        try:
            self.content_length = int(self.headers[b'Content-Length'])
        except KeyError:
            if self.http_verb in (b'POST', ):
                raise MissingContentLengthError()

        if len(self.body) < self.content_length:
            raise IncompleteRequestError('Found {0} bytes in body but expected {1}'.format(
                len(self.body), self.content_length))

        elif len(self.body) > self.content_length:
            raise InvalidRequestError('Found {0} bytes in body but expected {1}'.format(
                len(self.body), self.content_length))

    @classmethod
    def extract_request_components(cls, request_bytes):
        '''Extract and return HTTP request message components from the given binary data.

        Args:
            request_bytes (bytes): the HTTP request message

        Returns:
            (request_line, header_lines, body)
        '''
        binary_stream = io.BytesIO(request_bytes)
        request_line = binary_stream.readline()
        cls.validate_line_termination(request_line)

        header_lines = []
        line = binary_stream.readline()
        while line not in (b'\r\n', b''):
            cls.validate_line_termination(line)
            # continue extracting lines until we each an empty (delimiter-only) line
            header_lines.append(line)
            line = binary_stream.readline()

        if line == b'':
            raise IncompleteRequestError('Expected a blank line after request headers')

        body = binary_stream.read()

        return request_line, header_lines, body

    @staticmethod 
    def parse_request_line(line):
        tokens = line.rstrip().split(b' ')
        if len(tokens) == 3:
            http_verb, path, version = tokens
        else:
            raise InvalidRequestError("Invalid request line does not contain exactly 3 tokens")
        
        return http_verb, path, version

    @staticmethod
    def parse_header_lines(lines):
        headers = {}

        for line in lines:

            try:
                field_name, field_contents = line.split(b':', 1)
            except ValueError:
                raise InvalidRequestError('Expected a colon between request header name and value')

            field_contents = field_contents.strip()
            headers[field_name] = field_contents

        return headers

    @staticmethod
    def validate_line_termination(line, line_delimiter=b'\r\n'):
        if not line.endswith(line_delimiter):
            raise IncompleteRequestError("Incomplete line does not end with line delimiter")
