# -*- coding: utf-8 -*-
from get5W1H_with_translator import *
from flask import Flask, request
app = Flask(__name__)


@app.route('/get5w1h', methods=['POST']) #GET requests will be blocked
def get5w1h():
    req_data = request.get_json()

    text = req_data['text']
    lang = req_data['lang']
    result=extract_5W1H(text,lang)
    return result

if __name__ == '__main__':
   app.run()
