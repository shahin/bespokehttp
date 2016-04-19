'''A bespoke HTTP server.

Usage:
  server.py [--port=<num>]

Options:
  -h --help     Show this screen
  --port=<num>  The port number to listen on [default: 9191]

'''
import io
import socket

from docopt import docopt
from handler import CgiRequestHandler


class HttpServer(object):

    def __init__(self, host, port, handler_klass):
        self.host = host
        self.port = port
        self.handler_klass = handler_klass
        self.n_requests = 1

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port, ))

    def serve(self):
        self.socket.listen(self.n_requests)
        recv_buffer = io.BytesIO()
        
        conn, addr = self.socket.accept()

        while True:
            recv_data = conn.recv(1024)
            if recv_data:

                recv_buffer.write(recv_data)

                request_handler = self.handler_klass(recv_buffer.getvalue())
                response = request_handler.handle()
                if response:
                    recv_buffer = io.BytesIO()
                    conn.sendall(response)

if __name__ == '__main__':

    args = docopt(__doc__)

    HOST, PORT = 'localhost', int(args['--port'])
    server = HttpServer(HOST, PORT, CgiRequestHandler)
    server.serve()
