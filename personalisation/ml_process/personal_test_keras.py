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
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn import linear_model
from sklearn.externals import joblib
import datetime
from categories import *
from numpy import array
import keras
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
from pos_tagging import *
import multiprocessing as mp
from keras.models import load_model



# =============================================================================
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8') 
# 
# =============================================================================
t0=time.time()
#client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
client = MongoClient('mongodb://localhost:27017')
#db=client.way2
mdb=client["way2_personalize"]
#regx = re.compile("General", re.IGNORECASE)
#docs=db.master_prfsn_title_new.find({"level":3,"name":{"$nin":[regx]}},{"name":1})
#docs=db.master_prfsn_title.find({"name":{"$not":regx}},{"name":1,"_id":0})
#docs=mdb.not_standard_ptitle.find({})
custid=21887067
# =============================================================================
# x = datetime.datetime.now()
# today_date=str(x).split(" ")[0]
# seen_posts=mdb["user_data"].find({"custid" : custid,"date" :{'$in':["2019-03-13"]}},{"_id":0,"postid":1})
# sp=[]
# for pid in seen_posts:
#         sp.append(pid["postid"])
# =============================================================================
#cat_list=list(mdb["user_keywords_data"].find({"custid" : custid},{"_id":0,"category":1}))[0]["category"]     


documents=mdb.rating_points.find({"custid" : custid},{"category":1,"keywords":1,"post_desc":1,"rating":1})
docs=list(documents)
#test=mdb.posts_data.find({})

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

def new_stringify(cat,keys):
    #print(X)
    s=''
    if cat==cat: s=s+cat
    if keys==keys: s=s+keys
    return s
# =============================================================================
#     features=[]
#     for  i in range(len(X)):
#         #print(X.iloc[i,0],X.iloc[i,1])
#         s=''
#         if X.iloc[i,0]: s=s+str(X.iloc[i,0])
#         if X.iloc[i,1]: s=s+' '+' '.join(X.iloc[i,1])
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

X=[]
y=[]
    

def preprocess_pool(doc):
    s=''
    if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
    if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
    if "post_desc" in doc and doc["post_desc"]:
        #print(doc["post_desc"])
        #tag_list=[]
        #tag_list=pool.apply_async(tag,args=[doc["post_desc"]])
        #tags=pool.apply(tag,args=(doc["post_desc"]))
        tag_list=tag(doc["post_desc"])
        #print(tag_list)
        for t in tag_list:
            s=s+" "+t["word"]+"_"+t["tag"]
    return {"x":s,"y":doc["rating"]}
    
pool = mp.Pool(mp.cpu_count())

#results=[]
#for doc in docs[:20]:
#pool.apply_async(preprocess_pool,args=[doc],callback=results.append)
result=pool.map(preprocess_pool,docs)

df=pd.DataFrame(result)
X=df.iloc[:,0]
y=df.iloc[:,1]
#y=pool.map(preprocess_y,docs)

#print(X)
#print(y)
# =============================================================================
# for doc in docs:
#     #print(doc)
#     s=''
#     if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
#     if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
#     if "post_desc" in doc and doc["post_desc"]:
#         #print(doc["post_desc"])
#         #tag_list=[]
#         #tag_list=pool.apply_async(tag,args=[doc["post_desc"]])
#         #tags=pool.apply(tag,args=(doc["post_desc"]))
#         tag_list=tag(doc["post_desc"])
#         #print(tag_list)
#         for t in tag_list:
#             s=s+" "+t["word"]+"_"+t["tag"]
#     X.append(s)
#     y.append(doc["rating"])
# =============================================================================
pool.close()
pool.join()
#print(X[:2])


labels=y
#labels=keras.utils.to_categorical(y, num_classes=6)
vocab_size = len(X)*6
encoded_docs = [one_hot(d, vocab_size) for d in X]
#print(encoded_docs)
# pad documents to a max length of 4 words
max_length = 6
padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
t1=time.time()-t0
print("time taken for preprocess",t1)
#print(padded_docs)
# define the model
mt=time.time()
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=max_length))
model.add(Flatten())
#model.add(Dense(100, activation='relu'))
#model.add(Dense(50, activation='relu'))
model.add(Dense(6, activation='softmax'))
# compile the model
model.compile(
        optimizer=keras.optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False), 
        loss='sparse_categorical_crossentropy', 
        metrics=['acc'])
# summarize the model
print(model.summary())
# fit the model
model.fit(padded_docs, labels, epochs=10, verbose=0)
tmt=time.time()-mt
print("time taken for train:: ",tmt)

et=time.time()
# evaluate the model
loss, accuracy = model.evaluate(padded_docs, labels, verbose=0)
print('Accuracy: %f' % (accuracy*100))
tet=time.time()-et
print("time taken for evaluation:: ",tet)
#model.save(str(custid))






# =============================================================================
# t4=time.time()
# test_docs=mdb.rating_points_test.find({"custid" : custid},{"category":1,"keywords":1,"post_desc":1,"rating":1})
# test_x=[]
# test_y=[]
# pool = mp.Pool(mp.cpu_count())
# result=pool.map(preprocess_pool,test_docs)
# test_df=pd.DataFrame(result)
# test_x=df.iloc[:,0]
# test_y=df.iloc[:,1]
# pool.close()
# pool.join()
# # =============================================================================
# # for doc in test_docs:
# #     #print(doc)
# #     s=''
# #     if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
# #     if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
# #     if "post_desc" in doc and doc["post_desc"]:
# #         #print(doc["post_desc"])
# #         #tag_list=[]
# #         #tag_list=pool.apply_async(tag,args=[doc["post_desc"]])
# #         #tags=pool.apply(tag,args=(doc["post_desc"]))
# #         tag_list=tag(doc["post_desc"])
# #         #print(tag_list)
# #         for t in tag_list:
# #             s=s+" "+t["word"]+"_"+t["tag"]
# #     test_x.append(s)
# #     test_y.append(doc["rating"])
# # =============================================================================
# 
# #test_x=["రాజకీయాలు  telangana kaleshwaram godhavari ellampalli","వినోదం movies manmadhudu-2"]
# #test_x=X
# test_encoded_docs = [one_hot(d, vocab_size) for d in test_x]
# #print(test_encoded_docs)
# # pad documents to a max length of 4 words
# max_length = 6
# test_padded_docs = pad_sequences(test_encoded_docs, maxlen=max_length, padding='post')
# #print(test_padded_docs)
# #model=load_model(str(custid))
# 
# pred_y=model.predict_classes(test_padded_docs)
# #print(pred_y)
# t5=time.time()-t4
# print("time taken for test:: ",t5)
# 
# from sklearn.metrics import confusion_matrix 
# from sklearn.metrics import accuracy_score 
# from sklearn.metrics import classification_report 
# 
# results = confusion_matrix(test_y, pred_y) 
# print('Confusion Matrix :')
# print(results) 
# print('Accuracy Score :',accuracy_score(test_y, pred_y) )
# print('Report : ')
# print(classification_report(test_y, pred_y) )
# =============================================================================








