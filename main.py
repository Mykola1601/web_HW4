
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
# from time import sleep
import urllib.parse
import mimetypes
import threading
import pathlib
import logging
import socket
import pickle
import json

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('front-init/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('front-init/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('front-init/error.html', 404)


    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [
            el.split('=') for el in data_parse.split('&')]}
        # print(f'from "POST" {data_dict}')
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

        client1 = threading.Thread(target=client_sender, args=(HOST, PORT, data_dict ))
        client1.start()


    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def save_data(data):
    users = {}
    with open(FILE_NAME, "r") as fh:
        file = fh.read()
        if file:
            users = json.loads(file)
    with open(FILE_NAME, "w") as fh:
        users[str(datetime.now())] = data
        fh.write(json.dumps(users, indent=2))


def server_save(host, port):
    with socket.socket() as s:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if data:
                    data = pickle.loads(data)
                    print(f'From client: {data}')
                    conn.send(b"recived")
                    save_data(data=data)
                    data = None
                else:
                    s.close()
                    server_save(host, port)
                        



def client_sender(host, port, message : str =None  ):
    with socket.socket() as s:
        try:
            s.connect((host, port))
            s.sendall(  pickle.dumps(message) )
            data = s.recv(1024)
            print(f'From server: {data}')
        except ConnectionRefusedError:
            print('client exept')


if __name__ == '__main__':

    FILE_NAME = 'front-init/storage/data.json'
    HOST = '127.0.0.1'
    PORT = 5000
    users = {}

    server = threading.Thread(target=server_save, args=(HOST, PORT))
    server.start()

    run()
