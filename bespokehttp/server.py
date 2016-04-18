import io
import socket
from handler import HttpRequestHandler


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
        
        while True:
            conn, addr = self.socket.accept()
            recv_buffer.write(conn.recv(1024))

            request_handler = self.handler_klass(recv_buffer.getvalue())
            response = request_handler.handle()
            if response:
                print(response)
                conn.sendall(response)

if __name__ == '__main__':

    HOST, PORT = 'localhost', 9192
    server = HttpServer(HOST, PORT, HttpRequestHandler)
    server.serve()
