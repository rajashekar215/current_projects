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
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn import linear_model
from datetime import datetime, timedelta
import multiprocessing as mp
# =============================================================================
# from importlib import reload
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8') 
# =============================================================================


client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')

mdb=client["way2"]
user_rating_collection="user_data_new"
active_users_collection="active_users_new"
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
def generate_model(custid,last_post_time):
   # custid=17967798
    #x = datetime.now()
    #today_date=str(x).split(" ")[0]
    #yesterday=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    docs=mdb[user_rating_collection].find({"custid" : custid,"seen_unix_time":{'$gt':last_post_time}},{"category":1,"keywords":1,"rating":1,"seen_unix_time":1})
    #docs=mdb[user_rating_collection].find({"custid" : custid,"date" :{'$nin':["2019-03-07","2019-03-06"]}},{"category":1,"keywords":1,"rating":1})
    X=[]
    y=[]
    new_last_post_time=0
    for doc in docs:
        #print(doc)
        s=''
        if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
        X.append(s)
        y.append(doc["rating"])
        #print(custid,doc)
        new_last_post_time=doc['seen_unix_time']
    if len(X)>0:
        vectorizer = HashingVectorizer()
        vect_X=vectorizer.transform(X)
        #vectorizer = TfidfVectorizer()
        #vectorizer = CountVectorizer()
        #tfidf_model=vectorizer.fit_transform(X)
        #test_X=vectorizer.transform(tX)
        
        #from sklearn.linear_model import LogisticRegression
        #classifier = LogisticRegression(max_iter=500,random_state = 0,multi_class="multinomial",solver="lbfgs",penalty="l2")
        #classifier = LogisticRegression(max_iter=500,C=1000,solver='lbfgs')
        
        #classifier.fit(tfidf_model, y)
        #model=Pipeline([("tfidf",vectorizer),("lr",classifier)])
        #model=joblib.load("../models/"+str(custid))
        #model.partial_fit(vect_X,y)
        try:
            model=joblib.load("../models/"+str(custid))
            model.partial_fit(vect_X,y)
            joblib.dump(model, "../models/"+str(custid))
            print(str(custid)+"  partial_fit")
        except:
            if len(set(y))>1:
                print(str(custid)+" normal fit")
                model =linear_model.SGDClassifier(loss='log',penalty= "l2", n_iter=500,n_jobs=-1)
                model.fit(vect_X,y)
                joblib.dump(model, "../models/"+str(custid))
            else:
                print(str(custid)+" The number of classes has to be greater than one; got 1 class")
        #joblib.dump(vectorizer, "../models/vect_"+str(custid))
        print(custid+" last post time"+new_last_post_time)
        mdb[active_users_collection].update_one({"_id" : custid},{'$set':{'updated':1,'up_time':time.time(),'last_post_time':new_last_post_time}})
    else:
        print(str(custid)+" don't have atleast 1 flips")
        print(custid+" last post time"+new_last_post_time)
        mdb[active_users_collection].update_one({"_id" : custid},{'$set':{'updated':1,'up_time':time.time()}})

def user_model_update():
    print(sys.argv)
    t0=time.time()
    #active_users=mdb[active_users_collection].find({'updated':{'$in':[None,0]}}).limit(100)
    active_users=mdb[active_users_collection].find({'updated':int(sys.argv[1])}).limit(100)
    #active_users_df=pd.DataFrame(list(active_users))
    if active_users.count()>0:
        mode_gen_time={}
        pool = mp.Pool(mp.cpu_count())
        for user in active_users:
            t3=time.time()
            last_post_time=0
            if "last_post_time" in user and user["last_post_time"]:
                last_post_time=user["last_post_time"]
            #generate_model(int(user["_id"]),last_post_time)
            pool.apply(generate_model,args=(int(user["_id"]),last_post_time))
            t4=time.time()-t3
            print(user["_id"],"  models time ",t4)
            mode_gen_time[user["_id"]]=t4
        pool.close()
        print("models time ",mode_gen_time)
        #time.sleep(30)
        t1=time.time()-t0
        print("total time taken for 100  custids",t1)
        user_model_update()
    else:
        mdb[active_users_collection].update_many({},{'$set':{'updated':0}})
        print("no records waiting 10 seconds to retry")
        time.sleep(30)
        user_model_update()
    t1=time.time()-t0
    print("total time taken ",t1)
        
    
    
    

#time.sleep(10)
user_model_update()
#generate_model(17967798)

#pool = mp.Pool(mp.cpu_count())
#results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for user in data]
#pool.close()  