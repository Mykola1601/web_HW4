
from http.server import HTTPServer, BaseHTTPRequestHandler
from time import sleep
import urllib.parse
import mimetypes
import threading
import pathlib
import socket
import pickle
import json

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
        # print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        # print(data_parse)
        data_dict = {key: value for key, value in [
            el.split('=') for el in data_parse.split('&')]}
        print(f'from post {data_dict}')
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

        client = threading.Thread(target=client_sender, args=(HOST, PORT, data_dict))
        client.start()

        # client_sender(HOST, PORT, data_dict)


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
    print('start saving')
    with open(FILE_NAME, "a") as fh:
        json.dump(data, fh)
        fh.write(",\n")
    # return


def server_save(host, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(2)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if len(data) < 5:
                    # conn.send(b'1')
                    break
                data = pickle.loads(data)
                print(f'From client: {data}')
                save_data(data)
                print('writen')
                # break
                # conn.send(b'0')
                


def client_sender(host, port, message = None):
    if not message:
        return
    message = pickle.dumps(message)
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('in client')
        while True:
            try:
                s.connect((host, port))
                s.sendall( message )
                data = s.recv(1024)
                print(f'From server: {data}')
                break
            except ConnectionRefusedError:
                print('exeption')
                sleep(1)
                break


if __name__ == '__main__':

    FILE_NAME = 'data.json'
    HOST = '127.0.0.1'
    PORT = 5000

    server = threading.Thread(target=server_save, args=(HOST, PORT))
    # client = threading.Thread(target=client_sender, args=(HOST, PORT))

    server.start()
    # client.start()
    # server.join()
    # client.join()
    # print('Done!')

    run()
