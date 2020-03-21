from pymongo import MongoClient
from pprint import pprint
import collections
import re
import time
import sys
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
import string
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
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
user_rating_collection="user_data"
active_users_collection="userCustids"
# =============================================================================
# def stringify(X):
#     #print(X)
#     features=[]
#     for  i in range(len(X)):
#         print(X.iloc[i,0],X.iloc[i,1])
#         s=''
#         if X.iloc[i,0]==X.iloc[i,0]: s=s+str(X.iloc[i,0])
#         if X.iloc[i,1]==X.iloc[i,1]: s=s+' '+' '.join(X.iloc[i,1])
#         features.append(s)
#     return features
# =============================================================================

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
def generate_model(custid):
   # custid=17967798
    docs=mdb[user_rating_collection].find({"custid" : custid,"date" :{'$nin':[ "2019-02-25"]}},{"category":1,"keywords":1,"rating":1})
    
    X=[]
    y=[]
    for doc in docs:
        #print(doc)
        s=''
        if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
        X.append(s)
        y.append(doc["rating"])
    if len(set(y))>1:
        vectorizer = TfidfVectorizer()
        #vectorizer = CountVectorizer()
        #tfidf_model=vectorizer.fit_transform(X)
        #test_X=vectorizer.transform(tX)
        
        from sklearn.linear_model import LogisticRegression
        #classifier = LogisticRegression(max_iter=500,random_state = 0,multi_class="multinomial",solver="lbfgs",penalty="l2")
        classifier = LogisticRegression(max_iter=500,C=1000,solver='lbfgs')
        #classifier.fit(tfidf_model, y)
        model=Pipeline([("tfidf",vectorizer),("lr",classifier)])
        model.fit(X,y)
        joblib.dump(model, "../models/"+str(custid))
        mdb[active_users_collection].update_one({"_id" : custid},{'$set':{'status':1}})
    else:
        print(str(custid)+" don't have atleast 3 flips")


active_users=mdb[active_users_collection].find({})
#active_users_df=pd.DataFrame(list(active_users))
mode_gen_time={}
for user in active_users:
    t3=time.time()
    generate_model(int(user["_id"]))
    t4=time.time()-t3
    mode_gen_time[user["_id"]]=t4
    

t1=time.time()-t0
print("total time taken ",t1)
print("models time ",mode_gen_time)







