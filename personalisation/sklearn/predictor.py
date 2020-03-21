# -*- coding: utf-8 -*-
from pymongo import MongoClient
import time
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
import string
from nltk.stem import PorterStemmer
from sklearn.externals import joblib
from operator import itemgetter
from categories import *
# =============================================================================
# from importlib import reload
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8') 
# =============================================================================

t0=time.time()
client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')

mdb=client["way2"]


#docs=mdb.up_rating_feb_12.find({"custid" : 17967798})
todays_posts_collection="posts_data"
#user_rating_collection="up_rating_feb_12"
#active_users_collection="active_users_test"
def stringify(X):
    #print(X)
    features=[]
    for  i in range(len(X)):
        #print(X.iloc[i,0],X.iloc[i,1])
        s=''
        if X.iloc[i,0]: s=s+str(X.iloc[i,0])
        if X.iloc[i,1]: s=s+' '+' '.join(X.iloc[i,1])
        features.append(s)
    return features

def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    exclude = set(string.punctuation)
    text = ''.join(ch for ch in text if ch not in exclude)
    #text = text.translate(None, string.punctuation)
    tokens = word_tokenize(text)
    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]
    return tokens            

def predictions(custid):
    test=mdb[todays_posts_collection].find({})
    posts=[]
    post_data=[]
    for doc in test:
        #print(doc)
        s=''
        if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
        posts.append(s)
        post_data.append(doc)
    #post_data=pd.DataFrame(list(test))
    #tX=post_data.iloc[:,[1,2]]
    #posts=stringify(tX)
    #custid=17967798
    #print(custid)
    model=joblib.load("./models/"+str(custid))
    pred=model.predict(posts)
    #print(pred[20])
    ins_array=[]
    for i in range(len(pred)):
        #print(pred[i])
        post_doc=post_data[i]
        del post_doc['_id']
        postid=post_doc['postid']
        post_doc['postid']=int(postid)
        post_doc['custid']=custid
        post_doc['prediction']=int(pred[i])
        #print(post_doc)
        ins_array.append(post_doc)
    #print(ins_array)
    ins_array = sorted(ins_array, key=itemgetter('prediction'), reverse=True)
    #ret_array=[ x['postid'] for x in ins_array]
    return ins_array
    #mdb.pred_collection.insert_many(ins_array)
        
# =============================================================================
# model=joblib.load("./models/"+str(17967798))
# model.predict(["వార్తలు megastar pawan kalyan nagababu publicity pm janasena fans"
#  ,"వార్తలు  nagababu janasena megastar pawan kalyan"
#  ,"వార్తలు pawan kalyan nagababu janasena"
#  ,"బిజినెస్ icici tax pawan kalyan nagababu janasena"
#  ,"వార్తలు chandrababu naidu pawan kalyan nagababu janasena"
#  ])
# =============================================================================








