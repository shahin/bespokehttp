'''A bespoke HTTP server.

Usage:
  server.py [--port=<num>]

Options:
  -h --help     Show this screen
  --port=<num>  The port number to listen on [default: 9191]

'''
import io
import socket
import select

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
        
        open_sockets = []
        recv_buffers = {}

        while True:

            readable, writable, exceptional = select.select([self.socket] + open_sockets, [], [])

            for readable_socket in readable:

                if readable_socket is self.socket:
                    sock, addr = self.socket.accept()
                    open_sockets.append(sock)
                    recv_buffers[sock] = io.BytesIO()

                else:
                    recv_data = readable_socket.recv(1024)
                    if recv_data:

                        recv_buffers[readable_socket].write(recv_data)

                        request_handler = self.handler_klass(
                            recv_buffers[readable_socket].getvalue()
                        )
                        response = request_handler.handle()
                        print(response)
                        if response:
                            recv_buffers[readable_socket] = io.BytesIO()
                            readable_socket.sendall(response)

if __name__ == '__main__':

    args = docopt(__doc__)

    HOST, PORT = 'localhost', int(args['--port'])
    server = HttpServer(HOST, PORT, CgiRequestHandler)
    server.serve()
