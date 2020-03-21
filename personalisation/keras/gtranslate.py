from googletrans import Translator
import pandas as pd
import json,urllib.request
from fake_useragent import UserAgent
import ipaddress
import requests
import itertools
import random
ua= UserAgent().random

def proxy():
    response = requests.get("https://www.proxy-list.download/api/v1/get?type=http&anon=elite&country=in")
    proxy=(response.text)
    proxt_list= proxy.split('\r\n')
    proxy_dict= dict(itertools.zip_longest(*[iter(proxt_list)] * 2, fillvalue=""))
    return proxy_dict

proxy_dct=proxy()






def trns(aaa):
    translator = Translator(service_urls=['translate.google.com', 'translate.google.co.kr'],user_agent=ua ,proxies=proxy_dct)
    c= translator.translate(aaa,dest="te")
    content =c.text
    return content



