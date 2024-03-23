from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


import mimetypes
import urllib.parse
import pathlib
import socket
import logging

URI = "mongodb://mongodb:27017"


SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 3000


def send_data_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = SOCKET_HOST, SOCKET_PORT
    sock.sendto(data, server)
    sock.close()


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        router = urllib.parse.urlparse(self.path).path
        logging.info(router)
        match router:
            case "/":
                self.send_html("index.html")
            case "/message":
                self.send_html("message.html")
            case _:
                file = pathlib.Path(router[1:])
                if file.exists():
                    self.send_static()
                else:
                    self.send_html("error.html", 404)

    def send_html(self, filename, status=200):
        self.send_response(int(status))
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def send_static(self):
        self.send_response(200)
        mimetype = mimetypes.guess_type(self.path)
        if mimetype:
            self.send_header("Content-type", mimetype[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as f:
            self.wfile.write(f.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("0.0.0.0", 3000)
    httpd = server_class(server_address, handler_class)
    logging.info(f"starting server: {server_address}\n")

    try:
        httpd.serve_forever()
    except Exception as e:
        logging.error(e)
        httpd.server_close()


def save_data(data):
    client = MongoClient(URI, server_api=ServerApi("1"))
    db = client.final_project
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_parse = {
            "date": str(datetime.now()),
            **{
                key: value
                for key, value in [el.split("=") for el in data_parse.split("&")]
            },
        }
        db.messages.insert_one(data_parse)
    except Exception as e:
        logging.error(e)
    finally:
        client.close()


def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            save_data(data)
    except Exception as e:
        logging.error(e)
    finally:
        sock.close()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")

    pr_server = Process(target=run_http_server, args=(HTTPServer, HttpHandler))
    pr_server.start()
    pr_socket = Process(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    pr_socket.start()

    pr_server.join()
    pr_socket.join()
