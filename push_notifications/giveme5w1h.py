# -*- coding: utf-8 -*-

from Giveme5W1H.extractor.document import Document
from Giveme5W1H.extractor.extractor import MasterExtractor
from fake_useragent import UserAgent
from googletrans import Translator
import requests
import itertools
import sys
import time

extractor = MasterExtractor()

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
            print(q," ::  ",a)
        except:
            print(q," ::  ",None)


#tel_text='''జుక్కల్: కామారెడ్డి జిల్లా జుక్కల్ మండలం బస్వపూర్ గ్రామ పంచాయతీకి కేటాయించిన ట్రాక్టర్ ను గురువారం 
#బాన్సువాడ మహీంద్రా షో రూమ్ నుండి కొనుగోలు చేసినట్లు గ్రామ సర్పంచ్
#రవి శంకర్ పటేల్ తెలిపారు. ఈ సందర్భంగా ఆయన మాట్లాడుతూ ట్రాక్టర్ ను గ్రామ అభివృధి కొరకు మాత్రమే వాడతాము 
#అని అయన తెలిపారు.ఈ కార్యక్రమంలో గ్రామ సర్పంచ్, పంచాయతీ కార్యదర్శి ప్రకాష్, గ్రామస్థులు ఉన్నారు.'''

#tel_text=sys.argv[1]
#give5W1H(tel_text)
