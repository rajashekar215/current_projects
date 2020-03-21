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
from PIL import Image

result=[]
all_titles = []
Sorted_urls = []
result_links_jaccard = []

nlp = spacy.load("en_core_web_lg")

ua = str(UserAgent().random)

def proxy():
    response = requests.get("https://www.proxy-list.download/api/v1/get?type=http&a}non=elite&country=ru")
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

def get_keywords(eng_text,eng_text_heading):
    if eng_text != "":
        eng_text_local=eng_text.replace(",","").replace(":","").replace("'","").replace("(","").replace(")","")
        eng_text_local=re.sub(r'all_titles\.+[ ]*',".",eng_text_local)
        doc = nlp(eng_text_local)
    else:
        eng_text_heading=eng_text_heading.replace(",","").replace(":","").replace("'","").replace("(","").replace(")","")        
        doc = nlp(eng_text_heading)
        
    search_words = []
    sent = ""
    
    for i in doc:
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

def urlfinder(keywords):
    keywords=keywords
    logging.basicConfig(level=logging.DEBUG);
    logger = logging.getLogger(__name__)
   
    def search(keywords, max_results=None):
        url = 'https://duckduckgo.com/';
        params = {
        'q': keywords
        };
        logger.debug("Hitting DuckDuckGo for Token");
        #   First make a request to above URL, and parse out the 'vqd'
        #   This is a special token, which should be used in the subsequent request
        res = requests.post(url, data=params)
        searchObj = re.search(r'vqd=([\d-]+)\&', res.text, re.M|re.I);
        if not searchObj:
            logger.error("Token Parsing Failed !");
            return -1;
        logger.debug("Obtained Token");    
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
        logger.debug("Hitting Url : %s", requestUrl);
        i=0
        while i<10:
            j=0
            while j<10:
                try:
                    res = requests.get(requestUrl, headers=headers, params=params);
                    data = json.loads(res.text);
                    break;
                except ValueError as e:
                    logger.debug("Hitting Url Failure - Sleep and Retry: %s", requestUrl);
                    time.sleep(5);
                    continue;
                j=j+1  
            logger.debug("Hitting Url Success : %s", requestUrl);
            printJson(data["results"]);
           
            i=i+1
   
    imageurl=[]
    specs=[]
    title=[]
    
    def printJson(objs):
        for obj in objs:
            specs.append(("Width {0}, Height {1}".format(obj["width"], obj["height"])))
            title.append( ("Title {0}".format(obj["title"].encode('utf-8'))))
            imageurl.append((obj["image"]))     
            
    search(keywords)
    #print(imageurl)
    return imageurl[:10],specs[:10],title[:10]

def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2))) / float(len(s1.union(s2)))
  
def main_(text,title):
    eng_text= get_transalation(text)
    keywords=get_keywords(eng_text,'')
    eng_text_heading= get_transalation(title)
    keywords_heading= get_keywords('',eng_text_heading) 
    
    for i in range(len(keywords)):
        result.append(urlfinder(keywords[i]))
        
    for i in range(len(result)):
        for k in range(len(result[i][2])):
            titles=nlp(result[i][2][k].replace("Title b'","").replace("...",""))
            sent = ""
            for b in titles:
                if b.pos_ == 'PROPN':# or b.pos_ == 'NOUN': #or i.pos_ == 'VERB'or i.pos_ == 'ADJ':
                    sent+= b.text+" "
            t1=sent.split(" ")
            t2=keywords_heading.split(" ")
            if len(t2) == 1 : #some times heading might not contain any key word then we are extracting keywords out of text
                sent_text=""       
                for word in keywords:
                    sent_text = sent_text + word
                t2=sent_text.split(" ")  
                
            jsim=jaccard_similarity(t1, t2)
            
            if jsim>0.15:
                all_titles.append((result[i][0][k],result[i][1][k],sent,keywords[i],jsim))
    
    #Sorted_urls=sorted(all_titles,key=lambda x:x[3],reverse=True) 
    
    return all_titles

text="नई दिल्ली, एएनआइ। चीनी राष्ट्रपति शी चिनफिंग भारत दौरे पर आ रहे हैं। वह अक्टूबर के दूसरे हफ्ते में प्रधानमंत्री नरेंद्र मोदी के साथ चेन्नई के पास महाबलीपुरम का दौरा करेंगे। इस दौरान दोनों नेताओं की अनौपचारिक शिखर सम्मेलन के दौरान मुलाकात होगी। दोनों नेताओें के बीच यह दूसरी अनौपचारिक मुलाकात होगी। भारत की ओर मुलाकात की तारीखों की औपचारिक घोषणा होना अभी बाकी है"
title="इसी महीने भारत आएंगे चीनी राष्ट्रपतिचिनफिंग, PM मोदी से ऐतिहासिक महाबलीपुरम में होगी मुलाकात"

Sorted_urls=main_(text,title)

df_new = pd.DataFrame(Sorted_urls, columns =['Links', 'Dimensions','Images_str','Original_str','Jaccard_Score']) 
df_new = df_new.sort_values('Jaccard_Score',ascending=False)

result_links_jaccard = df_new["Links"].values.tolist()                   #### 1

new = df_new["Dimensions"].str.split(",", n = 1, expand = True) 

df_new["Width"]= new[0] 
df_new["Height"]= new[1] 

#df_new.drop(columns =["Dimensions"], inplace = True) 

df_new['Width'] = df_new['Width'].map(lambda x: x.lstrip('Width'))
df_new['Height'] = df_new['Height'].map(lambda x: x.lstrip(' Height'))

df_new['Width'] = df_new['Width'].astype('int')
df_new['Height'] = df_new['Height'].astype('int')

result_links_jaccard_dimension=[]
for index, row in df_new.iterrows():
    if row['Width'] <1000 or row["Height"]/row["Width"]>0.9:
        pass
    else:
        result_links_jaccard_dimension.append(row["Links"])              #### 2
      
from inltk.inltk import get_similar_sentences

# get similar sentences to the one given in hindi
output = get_similar_sentences(title, 5, 'hi')

translated_list=[]
for i in output:
    translatedtext=get_transalation(i)
    translated_list.append(translatedtext)
    
keywords_all=[]
for i in translated_list:
    keywordseach=get_keywords('',i)
    keywords_all.append(keywordseach)
    
result_nltk=[]
for i in range(len(keywords_all)):
    result_nltk.append(urlfinder(keywords_all[i]))

eng_text_heading= get_transalation(title)
keywords_heading= get_keywords('',eng_text_heading)       

all_titles_nltk_Jaccard=[]    
for i in range(len(result_nltk)):
    for k in range(len(result_nltk[i][2])):
        titles=nlp(result_nltk[i][2][k].replace("Title b'","").replace("...",""))
        sent = ""
        for b in titles:
            if b.pos_ == 'PROPN':# or b.pos_ == 'NOUN': #or i.pos_ == 'VERB'or i.pos_ == 'ADJ':
                sent+= b.text+" "
        t1=sent.split(" ")
        t2=keywords_heading.split(" ")#keywords[i].split(" ")
        jsim=jaccard_similarity(t1, t2)
        if jsim>0.15:
            all_titles_nltk_Jaccard.append((result_nltk[i][0][k],result_nltk[i][1][k],sent,keywords_heading,jsim))        

df_new_inlkt = pd.DataFrame(all_titles_nltk_Jaccard, columns =['Links', 'Dimensions','Images_str','Original_str','Jaccard_Score']) 
df_new_inlkt = df_new_inlkt.sort_values('Jaccard_Score',ascending=False)

result_links_inltk_Jaccard = df_new_inlkt["Links"].values.tolist()   #### 3

new_inltk = df_new_inlkt["Dimensions"].str.split(",", n = 1, expand = True) 

df_new_inlkt["Width"]= new_inltk[0] 
df_new_inlkt["Height"]= new_inltk[1] 

#df_new_inlkt.drop(columns =["Dimensions"], inplace = True) 

df_new_inlkt['Width'] = df_new_inlkt['Width'].map(lambda x: x.lstrip('Width'))
df_new_inlkt['Height'] = df_new_inlkt['Height'].map(lambda x: x.lstrip(' Height'))

df_new_inlkt['Width'] = df_new_inlkt['Width'].astype('int')
df_new_inlkt['Height'] = df_new_inlkt['Height'].astype('int')

result_links_inltk_jaccard_dimension=[]
for index, row in df_new_inlkt.iterrows():
    if row['Width'] <1000 or row["Height"]/row["Width"]>0.9:
        pass
    else:
        result_links_inltk_jaccard_dimension.append(row["Links"])   #### 4 

result_links_jaccard
result_links_jaccard_dimension
result_links_inltk_Jaccard
result_links_inltk_jaccard_dimension

print("----------------------------------------------------------------------------------")

print("result_links_jaccard is                  :", len(result_links_jaccard))
print("result_links_jaccard_dimension is        :", len(result_links_jaccard_dimension))
print("result_links_inltk_Jaccard is            :", len(result_links_inltk_Jaccard))
print("result_links_inltk_jaccard_dimension is  :", len(result_links_inltk_jaccard_dimension))

print("----------------------------------------------------------------------------------") 
              
####################################################################################################################################################################################################################################################################################################################################################################
        
#text1="नई दिल्ली, एएनआइ। चीनी राष्ट्रपति शी चिनफिंग भारत दौरे पर आ रहे हैं। वह अक्टूबर के दूसरे हफ्ते में प्रधानमंत्री नरेंद्र मोदी के साथ चेन्नई के पास महाबलीपुरम का दौरा करेंगे। इस दौरान दोनों नेताओं की अनौपचारिक शिखर सम्मेलन के दौरान मुलाकात होगी। दोनों नेताओें के बीच यह दूसरी अनौपचारिक मुलाकात होगी। भारत की ओर मुलाकात की तारीखों की औपचारिक घोषणा होना अभी बाकी है"
#title1="इसी महीने भारत आएंगे चीनी राष्ट्रपति चिनफिंग, PM मोदी से ऐतिहासिक महाबलीपुरम में होगी मुलाकातv"

#text2 = "जम्मू-कश्मीर के पुलवामा में 14 फरवरी को जब जैश-ए-मोहम्मद के आतंकियों ने CRPF के जवानों पर हमला किया था. तब पूरे देश में रोष था इसी के जवाब में भारतीय वायुसेना ने पाकिस्तान के बालाकोट में घुसकर एयरस्ट्राइक की थी. इस एयरस्ट्राइक में वायुसेना ने जैश-ए-मोहम्मद के आतंकी अड्डों पर ताबड़तोड़ बम बरसाए थे. अब शुक्रवार को वायुसेना की तरफ से इस एयरस्ट्राइक पर एक वीडियो जारी किया गया है. जिसमें एयरस्ट्राइक की पूरी प्रक्रिया को दिखाया गया है. (ये वीडियो प्रमोशनल है)"
#title2="ऐसे हुई थी बालाकोट में एयरस्ट्राइक, एयरफोर्स ने जारी किया VIDEO"

#text3 ="प्रधानमंत्री नरेंद्र मोदी ने ट्वीट किया, ‘अन्य भारतीयों की तरह, मैं भी #Solareclipse2019 के लिए उत्साहित था. हालांकि, मैं सूरज नहीं देख पाया क्योंकि यहां पूरी तरह से बादल छाए हुए हैं. लेकिन मैंने लाइव स्ट्रीम के जरिए कोझिकोडे में दिखाई दिए सूर्य ग्रहण का नजारा देखा. इसके साथ ही मैंने एक्सपर्ट्स के साथ बातकर इसके बारे में बातचीत की."
#title3="सूर्यग्रहण: PM मोदी ने देखा Ring Of Fire का नजारा, लिखा- मैं भी उत्साहित था"        
        
#text4 ="নাগরিকত্ব বিলের প্রতিবাদে উত্তাল রাজ্যের বিভিন্ন জেলা। পরিস্থিতি পর্যালোচনায় আগামিকাল রাজভবমে মুখ্যমন্ত্রী মমতা বন্দ্যোপাধ্যায়কে তলব করলেন রাজ্যপাল জগদীপ ধনখড়। এই নিয়ে আগে মুখ্যসচিব এবং ডিজিকে ডেকে পাঠিয়েছিলে তিনি। আজ সকাল ১০টা তাঁদের আসতে বলেছিলেন রাজ্যপাল। কিন্তু তাঁরা নির্ধারিত সময়ে দেখা করেননি। রাজ্যের মুখ্যসচিব ও ডিজির অনুপস্থিতিতে অসন্তুষ্ট হয়েছেন রাজ্যপাল। তার পরেই মুখ্যমন্ত্রীকে তলব করেন তিনি। তবে মুখ্যমন্ত্রী তাঁর সুবিধামতো সময়ে রাজভবনে আসতে বলেছেন তিনি।"
#title4="নাগরিকত্ব বিলের প্রতিবাদে উত্তাল রাজ্য, মুখ্যমন্ত্রীকে তলব রাজ্যপালের"        
        
#################################################################################################################################################################################################################################################################################################################################################################### 


