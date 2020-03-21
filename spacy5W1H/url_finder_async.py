import requests
import re
import json
import time
import logging
from fake_useragent import UserAgent
import itertools
import spacy
import pandas as pd
from googletrans import Translator
from flask import request, jsonify, Flask
import unicodedata
import re
from PIL import Image
import functools
import asyncio
import aiohttp



nlp = spacy.load("en_core_web_lg")

ua = str(UserAgent().random)

print("starting process")
def proxy():
    response = requests.get(
        "https://www.proxy-list.download/api/v1/get?type=http&a}non=elite&country=ru")
    proxy = (response.text)
    proxt_list = proxy.split('\r\n')
    proxy_dict = dict(itertools.zip_longest(
        *[iter(proxt_list)] * 2, fillvalue=""))
    return proxy_dict
proxy_dict = proxy()

def get_didyoumean(text):
    url = 'https://www.google.com/complete/search'
    params = {
        'source':'hp',
        'q': text,
        'cp': 5,
        'client':'psy-ab' ,
        'xssi': 't',
        'gs_ri': 'gws-wiz',
        'hl': 'en-IN',
        'authuser': 0
        }
    headers = {

        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'user-agent': ua,
        'accept': '*/*',
        'referer': 'https://www.google.com/',
        'sec-fetch-mode':'cors',
        'sec-fetch-site': 'same-origin',
        'scheme': 'https',
        'authority': 'www.google.com'
       
        }
    res = requests.get(url, headers=headers,params=params, proxies=proxy_dict)
    data = res.text
    # data = data.encode('utf-8').decode('unicode-escape')
    # data= data.replace('<b>','')
    # data = data.replace('<\/b>','')
    #result = re.search('"(.*)"', data)
    #print(result.group(1))
    data= str(data).replace(")]}'", '')
    structd = json.loads(data)
    len_structd= len(structd[0])

    try: 
        txt = structd[0][0][0]
        txt=str(txt).replace('<b>','')
        txt=str(txt).replace('</b>','')
        txt = txt.split(',')
        txt = txt[0]
    except:
        txt = text


   
    # txt = structd0 +','+ structd1 +','+ structd2+ ','+structd3
   
    return txt



    

def fetchdata(objs, max_v):
    width=[]
    height=[]
    thumbnai_url=[]
    page_url=[]
    title=[]
    image_url=[]
    count= 0

    for obj in objs:
        if obj["width"] <1000 or count>=max_v or obj["height"]/obj["width"]>0.9:
            pass
        else:
            width.append(obj["width"])
            height.append(obj["height"])
            thumbnai_url.append(obj["thumbnail"])
            page_url.append(obj["url"])
            title.append(obj["title"].encode('utf-8'))
            image_url.append(obj["image"])
            count= count+1
    df= pd.DataFrame(list(zip( width,height,thumbnai_url,page_url,title,image_url)),columns=['width','height','thumbnai_url','page_url','title','image_url'])  
    return df
        

async def get_transalation(text1):
    final_text=[]
    try:
        text1= text1.replace('।','.')
        text1=text1.split('.')
        print("trns - start ")
        func = functools.partial(Translator,service_urls=['translate.google.co.in', 'translate.google.com'], user_agent=ua, proxies=proxy_dict)
        translator = await loop.run_in_executor(None,func)
        for txt in text1:
            transalation1= translator.translate(txt, dest="en" )
            eng_text= transalation1.text
            final_text.append(eng_text)

        
        final_text=('. '.join(final_text))
        print(final_text)
        print("trns - end ")
        return final_text

    except Exception as e:
        print(e)
        pass



def get_keywords(eng_text):
    eng_text=eng_text.replace(",","").replace(":","").replace("'","").replace("(","").replace(")","")
    eng_text=re.sub(r'all_titles\.+[ ]*',".",eng_text)
    #sentences=eng_text.split(".")
    doc = nlp(eng_text)
    search_words = []
    new_list = []
    sent = ""
    for i in doc:
        #if i.text=="meeting":
        #print(i.text)
        if i.pos_ == 'PROPN':#or i.pos_ == 'NOUN' or i.pos_ == 'VERB':#or i.pos_ == 'ADJ':
            sent+= i.text+" "
        if i.text=="." and sent!="":
            search_words.append(sent)
            sent =""
    if len(search_words)== 0:
        return sent
        #search_words.append(sent)
    else:
        return search_words


async def urlfinder(session,keywords):
        keywords=keywords
        #logging.basicConfig(level=logging.DEBUG);
        #logger = logging.getLogger(__name__)
        print("keyword ",keywords," started")
        async def search(keywords, max_results=None):
                #executor = ThreadPoolExecutor(2)
                #loop = asyncio.get_event_loop()
                url = 'https://duckduckgo.com/';
                params = {
                'q': keywords
                };
           
                #logger.debug("Hitting DuckDuckGo for Token");
       
        #   First make a request to above URL, and parse out the 'vqd'
        #   This is a special token, which should be used in the subsequent request
                #res = requests.post(url, data=params)
# =============================================================================
#                 func = functools.partial(requests.post,url=url, data=params)
#                 req=loop.run_in_executor(None,func)
#                 res = await req
# =============================================================================
                async with session.post(url, data=params) as response:
                    res= await response.text()
                    searchObj = re.search(r'vqd=([\d-]+)\&', res, re.M|re.I);
           
                    if not searchObj:
                        #logger.error("Token Parsing Failed !");
                        return -1;
           
                    #logger.debug("Obtained Token");    
                    headers = {
                            'dnt': '1',
                            #'accept-encoding': 'gzip, deflate, sdch, br',
                            'x-requested-with': 'XMLHttpRequest',
                            'accept-language': '*',
                            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                            'accept': 'application/json, text/javascript, */*; q=0.01',
                            'referer': 'https://duckduckgo.com/',
                            'authority': 'duckduckgo.com',
                        }
               
                    params = (
                    ('l', 'wt-wt'),
                    ('o', 'json'),
                    ('q', keywords),
                    ('vqd', searchObj.group(1)),
                    ('f', ',,,'),
                    ('p', '2')
                    )
           
                    requestUrl = url + "i.js";
           
                    #logger.debug("Hitting Url : %s", requestUrl);
                    i=0
                    while i<10:
                        j=0
                        while j<10:
                            #print("hitting for keyword:: ",requestUrl)
                            try:
    # =============================================================================
    #                             func = functools.partial(requests.get,url=requestUrl, headers=headers, params=params)
    #                             req=loop.run_in_executor(None,func)
    #                             res = await req
    # =============================================================================
                                async with session.get(url=requestUrl, headers=headers, params=params) as response:
                                    res= await response.text()
                                    data = json.loads(res);
                                    break;
                            except ValueError as e:
                                #logger.debug("Hitting Url Failure - Sleep and Retry: %s", requestUrl);
                                await asyncio.sleep(0.1);
                                continue;
                            j=j+1  
                        #logger.debug("Hitting Url Success : %s", requestUrl);
                        await printJson(data["results"]);
                       
                        i=i+1
           
            #requestUrl = url + data["next"];
        imageurl=[]
        specs=[]
        title=[]
        async def printJson(objs):
                for obj in objs:
                    specs.append(("Width {0}, Height {1}".format(obj["width"], obj["height"])))
                    #print("Thumbnail {0}".format(obj["thumbnail"]))
                    #print("Url {0}".format(obj["url"]))
                    title.append( ("Title {0}".format(obj["title"].encode('utf-8'))))
                    #print ("Image {0}".format(obj["image"]))
                    imageurl.append((obj["image"]))          
       
    #print(search("अजित पवार के इस्तीफा देने के बाद"))
        await search(keywords)
        #print(imageurl)
        print("keyword ",keywords," finished")
        return imageurl[:10],specs[:10],title[:10]
    

def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2))) / float(len(s1.union(s2)))
  

async def main_(text):
        eng_text=await get_transalation(text)
        keywords=get_keywords(eng_text)
        #image_list=get_image(keywords, 5)
        main_url = []
        result=[]
        all_titles = []
        Sorted_urls = []
# =============================================================================
#         for i in range(len(keywords)):
#             main_url = await urlfinder(keywords[i])
#             result.append(main_url)
# =============================================================================
# =============================================================================
#         res_loop=[urlfinder(keywords[i]) for i in range(len(keywords))]
#         result=await asyncio.gather(*res_loop)
# =============================================================================
        
        tasks=[]
        async with aiohttp.ClientSession() as session:
            for i in range(len(keywords)):
                tasks.append(urlfinder(session, keywords[i]))
            result = await asyncio.gather(*tasks)
            #return result
            print(result)
            for i in range(len(result)):
                for k in range(len(result[i][2])):
                    titles=nlp(result[i][2][k].replace("Title b'","").replace("...",""))
                    sent = ""
                    for b in titles:
                        if b.pos_ == 'PROPN':# or b.pos_ == 'NOUN': #or i.pos_ == 'VERB'or i.pos_ == 'ADJ':
                            sent+= b.text+" "
                    t1=sent.split(" ")
                    t2=keywords[i].split(" ")
                    jsim=jaccard_similarity(t1, t2)
                    if jsim>0.2:
                        all_titles.append((result[i][0][k],result[i][1][k],sent,keywords[i],jsim))
            
            Sorted_urls=sorted(all_titles,key=lambda x:x[4],reverse=True) 
            print(Sorted_urls)
            return Sorted_urls
            

#text='নাগরিকত্ব বিলের প্রতিবাদে উত্তাল রাজ্যের বিভিন্ন জেলা। পরিস্থিতি পর্যালোচনায় আগামিকাল রাজভবমে মুখ্যমন্ত্রী মমতা বন্দ্যোপাধ্যায়কে তলব করলেন রাজ্যপাল জগদীপ ধনখড়। এই নিয়ে আগে মুখ্যসচিব এবং ডিজিকে ডেকে পাঠিয়েছিলে তিনি। আজ সকাল ১০টা তাঁদের আসতে বলেছিলেন রাজ্যপাল। কিন্তু তাঁরা নির্ধারিত সময়ে দেখা করেননি। রাজ্যের মুখ্যসচিব ও ডিজির অনুপস্থিতিতে অসন্তুষ্ট হয়েছেন রাজ্যপাল। তার পরেই মুখ্যমন্ত্রীকে তলব করেন তিনি। তবে মুখ্যমন্ত্রী তাঁর সুবিধামতো সময়ে রাজভবনে আসতে বলেছেন তিনি।'
text="नई दिल्ली, एएनआइ। चीनी राष्ट्रपति शी चिनफिंग भारत दौरे पर आ रहे हैं। वह अक्टूबर के दूसरे हफ्ते में प्रधानमंत्री नरेंद्र मोदी के साथ चेन्नई के पास महाबलीपुरम का दौरा करेंगे। इस दौरान दोनों नेताओं की अनौपचारिक शिखर सम्मेलन के दौरान मुलाकात होगी। दोनों नेताओें के बीच यह दूसरी अनौपचारिक मुलाकात होगी। भारत की ओर मुलाकात की तारीखों की औपचारिक घोषणा होना अभी बाकी है"

#images =main_(text)

#Sorted_urls=await main_(text)

t1=time.time()
loop = asyncio.get_event_loop()
Sorted_urls=loop.run_until_complete(main_(text))
print("Time taken:: ",time.time()-t1)
print("completed::\n",Sorted_urls)
#loop.close()


