from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import json
import mimetypes
import urllib.parse
import pathlib
import socket
import logging

uri = "mongodb://mongodb:27017"
