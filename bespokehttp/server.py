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

        while True:
            try:
                conn, addr = self.socket.accept()
                request_data = conn.recv(1024)
                if request_data:
                    request_handler = self.handler_klass(request_data)
                    request_handler.handle()
                    request_handler.wfile.seek(0)
                    conn.sendall(request_handler.wfile.read())
            except KeyboardInterrupt:
                break
        
        self.socket.close()


if __name__ == '__main__':

    HOST, PORT = 'localhost', 9191
    server = HttpServer(HOST, PORT, HttpRequestHandler)
    server.serve()
