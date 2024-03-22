from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pathlib import Path


import json
import mimetypes
import urllib.parse
import pathlib
import socket
import logging

uri = "mongodb://mongodb:27017"

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 4000

BASE_DIR=Path(__file__).parent

def send_data_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = SOCKET_HOST, SOCKET_PORT
    sock.sendto(data, server)
    sock.close()

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        pass

    def do_GET(self):
        router = urllib.urlparse(self.path).path
        match router:
            case "/":
                self.send_html("index.html")
            case "/message":
                self.send_html("message.html")
            case _:
                file = BASE_DIR.joinpath(router[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)
