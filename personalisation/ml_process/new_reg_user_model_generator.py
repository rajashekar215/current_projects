# -*- coding: utf-8 -*-

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
import MySQLdb
import contextlib
#import pickle 

# =============================================================================
# from importlib import reload
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8') 
# =============================================================================

# =============================================================================
# client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
# #client = MongoClient('mongodb://localhost:27017/')
# 
# 
# mdb=client["way2"]
# user_rating_collection="user_data_new"
# active_users_collection="active_users_new"
# =============================================================================
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
    client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
    #client = MongoClient('mongodb://localhost:27017/')
    
    
    mdb=client["way2"]
    user_rating_collection="user_data_new"
    active_users_collection="active_users_new"
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
        print("before try in generate model")
        try:
            with open("../models/"+str(custid),'wb+') as f:
                #f = open("../models/"+str(custid),'wb+')
                model=joblib.load(f)
                model.partial_fit(vect_X,y)
                joblib.dump(model, f)
                #f.close()
                print(str(custid)+"  partial_fit")
            
        except Exception as e: 
            print("exception in generate model",e)
            if len(set(y))>1:
                print(str(custid)+" normal fit")
                model =linear_model.SGDClassifier(loss='log',penalty= "l2", n_iter=500,n_jobs=-1)
                model.fit(vect_X,y)
                with open("../models/"+str(custid),'wb+') as f:
                    #f = open("../models/"+str(custid),'wb+')
                    joblib.dump(model, f)
                    #f.close()
            else:
                print(str(custid)+" The number of classes has to be greater than one; got 1 class")
        #joblib.dump(vectorizer, "../models/vect_"+str(custid))
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"_id" : custid},{'$set':{'updated':1,'up_time':time.time(),'last_post_time':new_last_post_time,"reg_date":str(datetime.now()).split(" ")[0]}},upsert=True)
        client.close()
    else:
        print(str(custid)+" don't have atleast 1 flips")
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"_id" : custid},{'$set':{'updated':1,'up_time':time.time(),"reg_date":str(datetime.now()).split(" ")[0]}},upsert=True)
        client.close()

def user_model_update(start,end):
    client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
    #client = MongoClient('mongodb://localhost:27017/')
    mdb=client["way2"]
    user_rating_collection="user_data_new"
    active_users_collection="active_users_new"
    mydb = MySQLdb.connect(
      host="49.156.128.100",
      user="way2sms",
      passwd="waysmsawd#$%@",
      database="way2app",
      charset='utf8',
    )
    mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    print(sys.argv)
    t0=time.time()
    x = datetime.now()
    today_date=str(x).split(" ")[0]
    print(today_date)
    timestamp=time.mktime(datetime.strptime(today_date, "%Y-%m-%d").timetuple())
    print(timestamp)
    query="SELECT custid FROM way2app.login_reg_"+str(today_date.split("-")[1]).replace("0","")+"_"+today_date.split("-")[0]+" where a_date>"+str(int(timestamp))+"  and (activity = 'newsreg' or activity = 'newsoldreg' ) ORDER BY sno DESC limit "+str(start)+","+str(end)+";"
    print(query)
    try:
        mycursor.execute(query)
        new_reg_user = mycursor.fetchall()
        
        #mydb.close()
        #active_users=mdb[active_users_collection].find({'updated':{'$in':[None,0]}}).limit(100)
        #active_users=mdb[active_users_collection].find({'updated':int(sys.argv[1])}).limit(100)
        #active_users_df=pd.DataFrame(list(active_users))
        if len(new_reg_user)>0:
            print("new reg count>0")
            mode_gen_time={}
            #pool = mp.Pool(mp.cpu_count())
            num_cpus = mp.cpu_count()
            print("pool created")
            for user in new_reg_user:
                print(user["custid"])
                t3=time.time()
                last_post_time=0
                auc=list(mdb[active_users_collection].find({"_id" : int(user["custid"])}))
                if len(auc)>0 and "last_post_time" in auc[0] and auc[0]["last_post_time"]:
                    last_post_time=auc[0]["last_post_time"]
                #generate_model(int(user["custid"]),last_post_time)
                print("before pool apply")
                with contextlib.closing(mp.Pool(processes=num_cpus)) as pool:
                    pool.apply(generate_model,args=(int(user["custid"]),last_post_time))
                t4=time.time()-t3
                print(user["custid"],"  models time ",t4)
                mode_gen_time[user["custid"]]=t4
            pool.close()
            print("pool closed")
            #print("models time ",mode_gen_time)
            #time.sleep(30)
            t1=time.time()-t0
            print("total time taken for 100  custids",t1)
            mycursor.close()
            client.close()
            mydb.close()
            user_model_update(int(start)+int(end),100)
        else:
            mycursor.close()
            client.close()
            mydb.close()
            #mdb[active_users_collection].update_many({},{'$set':{'updated':0}})
            print("no records waiting 10 seconds to retry")
            
            time.sleep(10)
            user_model_update(0,100)
        t1=time.time()-t0
        print("total time taken ",t1)
    except Exception as e: 
        print(e)
        print("mysql exception")
        mycursor.close()
        client.close()
        mydb.close()
        time.sleep(10)
        user_model_update(start,end)
        
    
    
    

#time.sleep(10)
user_model_update(0,100)
#generate_model(17967798)

#pool = mp.Pool(mp.cpu_count())
#results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for user in data]
#pool.close()  


# =============================================================================
# import contextlib
# num_cpus = multiprocessing.cpu_count()
# with contextlib.closing(multiprocessing.Pool(processes=num_cpus)) as pool:
#     data = pool.map(get_output_from_input, input_data)
#     return itertools.chain.from_iterable(data)
# =============================================================================
