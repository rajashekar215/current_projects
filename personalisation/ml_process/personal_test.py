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
#cat_list=list(mdb["rating_points"].find({"custid" : custid},{"_id":0,"category":1}))[0]["category"]     


docs=mdb.rating_points.find({"custid" : custid},{"category":1,"keywords":1,"rating":1})
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
for doc in docs:
    #print(doc["category"],doc["keywords"])
    s=''
    if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
    if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
    X.append(s)
    y.append(doc["rating"])

# =============================================================================
# tX=[]
# for doc in test:
#     tX.append(new_stringify(doc["category"],doc["keywords"]))
# =============================================================================

# =============================================================================
# df=pd.DataFrame(list(docs))
# X=df.iloc[:,[1,4]]
# X=stringify(X)
# y=df.iloc[:,6]
# 
# tdf=pd.DataFrame(list(test))
# tX=tdf.iloc[:,[1,2]]
# tX=stringify(tX)
# =============================================================================


#vectorizer = TfidfVectorizer()
#vectorizer = CountVectorizer()
#tfidf_model=vectorizer.fit_transform(X)
#test_X=vectorizer.transform(tX)

# =============================================================================
# from sklearn.linear_model import LogisticRegression
# #classifier = LogisticRegression(max_iter=500,random_state = 0,multi_class="multinomial",solver="lbfgs",penalty="l2")
# classifier = LogisticRegression(max_iter=100, C=1000,solver='lbfgs')
# 
# model=Pipeline([("tfidf",vectorizer),("lr",classifier)])
# model.fit(X,y)
# =============================================================================
#classifier.fit(tfidf_model, y)
t1=time.time()-t0
print("time taken ",t1)

# =============================================================================
# X=["News chandrababu tdp"
# ,"News chandrababu oscar wards"
# ,"News chandrababu ktr"
# ,"News kcr"
# ]
# y=[1,1,1,1]
# =============================================================================
vectorizer = HashingVectorizer()
vect_X=vectorizer.transform(X)
model =linear_model.SGDClassifier(loss='log',penalty= "l2", n_iter=1000)
model.fit(vect_X,y)

pred_y=model.predict(vect_X)

from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 

results = confusion_matrix(y, pred_y) 
print('Confusion Matrix :')
print(results) 
print('Accuracy Score :',accuracy_score(y, pred_y) )
print('Report : ')
print(classification_report(y, pred_y) )
# =============================================================================
# 
# from sklearn.naive_bayes import MultinomialNB
# classifier = MultinomialNB()
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================



# =============================================================================
# from xgboost import XGBClassifier
# classifier=XGBClassifier(max_depth=100, n_estimators=100)
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================
# =============================================================================
# 
# from sklearn.ensemble import RandomForestClassifier
# classifier= RandomForestClassifier()
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================

# =============================================================================
# from sklearn.tree import DecisionTreeClassifier
# classifier = DecisionTreeClassifier()
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================

# =============================================================================
# from sklearn.neighbors import KNeighborsClassifier
# classifier = KNeighborsClassifier(n_neighbors=5)
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================

# =============================================================================
# from sklearn import svm
# classifier= svm.SVC(gamma='scale', decision_function_shape='ovo',C=10000)
# classifier.fit(tfidf_model, y)
# t1=time.time()-t0
# print("time taken ",t1)
# =============================================================================


t2=time.time()
#pred=model.predict(tX)
#pred=classifier.predict(test_X)
t3=time.time()-t2
print("time taken ",t3)

#train_pred=classifier.predict(tfidf_model)

# =============================================================================
# t1=vectorizer.transform(["News megastar pawan kalyan nagababu publicity pm janasena fans"
# ,"News  nagababu janasena megastar pawan kalyan"
# ,"News pawan kalyan nagababu janasena"
# ,"బిజినెస్ icici tax pawan kalyan nagababu janasena"
# ,"News chandrababu naidu pawan kalyan nagababu janasena"
# ])
# =============================================================================
#classifier.predict(t1)   
#t1=vectorizer.transform(["వార్తలు  nagababu janasena megastar pawan kalyan"])

#t1=vectorizer.transform(["వార్తలు pawan kalyan nagababu janasena"])
# =============================================================================
# print(model.predict(vectorizer.transform(["వార్తలు megastar pawan kalyan nagababu publicity pm janasena fans"
# ,"వార్తలు  nagababu janasena megastar pawan kalyan"
# ,"వార్తలు pawan kalyan nagababu janasena"
# ,"బిజినెస్ icici tax pawan kalyan nagababu janasena"
# ,"వార్తలు chandrababu naidu pawan kalyan nagababu janasena"
# ])))
# =============================================================================
X=["News chandrababu tdp"
,"News chandrababu oscar wards"
,"News chandrababu ktr"
,"News kcr"
]
y=[1,1,0,1]
vectorizer = HashingVectorizer()
vect_X=vectorizer.transform(X)
model.partial_fit(vect_X,y)
joblib.dump(model, "../models/test_"+str(custid))
tmodel=joblib.load("../models/test_"+str(custid))
print(tmodel.predict(vectorizer.transform(["News chandrababu tdp"
,"News chandrababu oscar wards"
,"News chandrababu ktr"
,"News kcr"
])))

#t1_pred=classifier.predict(t1)


t4=time.time()
test_docs=mdb.rating_points_test.find({"custid" : custid},{"category":1,"keywords":1,"post_desc":1,"rating":1})
test_x=[]
test_y=[]
# =============================================================================
# pool = mp.Pool(mp.cpu_count())
# result=pool.map(preprocess_pool,test_docs)
# test_df=pd.DataFrame(result)
# test_x=df.iloc[:,0]
# test_y=df.iloc[:,1]
# pool.close()
# pool.join()
# =============================================================================
for doc in test_docs:
    #print(doc)
    s=''
    if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
    if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
    #if "post_desc" in doc and doc["post_desc"]:
        #s=s+" "+doc["post_desc"]
# =============================================================================
#         #print(doc["post_desc"])
#         #tag_list=[]
#         #tag_list=pool.apply_async(tag,args=[doc["post_desc"]])
#         #tags=pool.apply(tag,args=(doc["post_desc"]))
#         #tag_list=tag(doc["post_desc"])
#         #print(tag_list)
#         #for t in tag_list:
#             #s=s+" "+t["word"]+"_"+t["tag"]
# =============================================================================
    test_x.append(s)
    test_y.append(doc["rating"])
    
vectorizer1 = HashingVectorizer()
vect_test_X=vectorizer1.transform(test_x)

pred_y=model.predict(vect_test_X)


results = confusion_matrix(test_y, pred_y) 
print('Confusion Matrix :')
print(results) 
print('Accuracy Score :',accuracy_score(test_y, pred_y) )
print('Report : ')
print(classification_report(test_y, pred_y) )





