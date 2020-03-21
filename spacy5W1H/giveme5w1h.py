# -*- coding: utf-8 -*-
from Giveme5W1H.extractor.preprocessors.preprocessor_core_nlp import Preprocessor
preprocessor = Preprocessor('http://49.156.128.11:9000')
#MasterExtractor(preprocessor=preprocessor)
from Giveme5W1H.extractor.document import Document
from Giveme5W1H.extractor.extractor import MasterExtractor
from fake_useragent import UserAgent
from googletrans import Translator
import requests
import itertools
import sys
import time

extractor = MasterExtractor(preprocessor=preprocessor)

ua = str(UserAgent().random)
#ua='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0'

def proxy():
    response = requests.get("https://www.proxy-list.download/api/v1/get?type=http&a}non=elite&country=in")
    proxy = (response.text)
    proxt_list = proxy.split('\r\n')
    proxy_dict = dict(itertools.zip_longest(
        *[iter(proxt_list)] * 2, fillvalue=""))
    return proxy_dict
proxy_dict = proxy()

def get_transalation(text1):
    final_text=[]
    try:
        text1= text1.replace('।','.')
        text1=text1.split('.')
        translator = Translator(service_urls=['translate.google.co.in', 'translate.google.com'], user_agent=ua, proxies=proxy_dict)
        for txt in text1:
            transalation1= translator.translate(txt, dest="en" )
            eng_text= transalation1.text
            final_text.append(eng_text)

        final_text=('. '.join(final_text))
        
        return final_text

    except Exception as e:
        print(e)
        pass

def give5W1H(tel_text):
    out_dict={}
    #print(tel_text)
    eng_text=get_transalation(tel_text)
    #print(eng_text)
    st=time.time()
    doc = Document.from_text(eng_text)
    # or: doc = Document(title, lead, text, date_publish) 
    doc = extractor.parse(doc)
    print(time.time()-st)
    for q in ['who','what','when','where','why','how']:
        try:
            a = doc.get_top_answer(q).get_parts_as_text()
            out_dict[q]=a
            #print(q," ::  ",a)
        except:
            out_dict[q]=None
            #print(q," ::  ",None)
    return out_dict
