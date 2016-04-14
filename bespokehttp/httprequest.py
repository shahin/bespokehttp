class BadRequestError(Exception):
    pass

class HttpRequest(object):

    def __init__(self, request_data):
        self.data = request_data

        # handle both LF- and CRLF-delimited requests
        lines = [line.rstrip('\r') for line in self.data.split('\n')]

        self.request_line = lines[0]
        self.header_lines = []
        self.body_lines = []

        if len(lines) > 1:

            lines_generator = (line for line in lines[1:])
            for line in lines_generator:
                if len(line) == 0:
                    break
                else:
                    self.header_lines.append(line)

            self.body_lines = [line for line in lines_generator]

        self.http_verb, self.path, self.version = self.parse_request_line(self.request_line)
        self.headers = self.parse_header_lines(self.header_lines)

    @staticmethod 
    def parse_request_line(line):
        tokens = line.split(' ')
        if len(tokens) == 3:
            http_verb, path, version = tokens
        else:
            raise BadRequestError("Invalid header.")
        
        return http_verb, path, version

    @staticmethod
    def parse_header_lines(lines):
        headers = {}
        token_sep = ' '

        for line in lines:
            field_name, field_contents = line.split(token_sep, ' ', 1)
            field_name = field_name.rstrip(':')
            headers[field_name] = field_contents

        return headers
