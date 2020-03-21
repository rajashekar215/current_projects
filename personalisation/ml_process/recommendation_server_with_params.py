# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from bson import json_util
import json
from predictions_corrected import *

HOST_NAME = '49.156.128.105'
#HOST_NAME = 'localhost'
#HOST_NAME = '172.16.20.212'
PORT_NUMBER = 9000


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        print(query_components)
        if query_components and query_components['custid']:
            args={}
            args['custid']=int(query_components['custid'][0])
            if 'langId' in query_components:args['lang_id']=int(query_components['langId'][0])
            if 'categoryid' in query_components:args['categoryid']=int(query_components['categoryid'][0]) 
            if 'request_source' in query_components:args['request_source']=query_components['request_source'][0]
            else:args['request_source']=""
            if 'userEditions' in query_components:args['userEditions']=query_components['userEditions'][0] 
            else:args['userEditions']=""
            if 'userMandals' in query_components:args['userMandals']=query_components['userMandals'][0] 
            if 'userVillages' in query_components:args['userVillages']=query_components['userVillages'][0] 
            if 'singleDistrict' in query_components:args['singleDistrict']=query_components['singleDistrict'][0] 
            if 'pageid' in query_components:args['pageid']=query_components['pageid'][0] 
            if 'limit' in query_components:args['limit']=query_components['limit'][0] 
            if 'currentPostTime' in query_components:args['currentPostTime']=query_components['currentPostTime'][0] 
            if 'lastpostid' in query_components:args['lastpostid']=query_components['lastpostid'][0] 

            preds=predictions(**args)
            #preds=predictions(query_components['custid'][0])
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(preds, default=json_util.default), 'UTF-8'))
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