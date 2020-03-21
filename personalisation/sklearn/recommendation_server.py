# -*- coding: utf-8 -*-

import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from predictor import *

HOST_NAME = '49.156.128.105'
#HOST_NAME = 'localhost'
PORT_NUMBER = 8000


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        print(query_components)
        if query_components and query_components['custid']:
            preds=predictions(query_components['custid'][0])
            preds=[ x['postid'] for x in preds]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(preds), 'UTF-8'))
        else:
            print(query_components)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes("please enter custid", 'UTF-8'))
       


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))