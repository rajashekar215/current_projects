from pymongo import MongoClient
import collections
import re
import sys
import numpy as np
import pandas as pd
import datetime
#from categories import *
from numpy import array
import keras
from keras.models import Sequential
from keras.layers import Dense,Conv1D,GlobalMaxPooling1D
#from pos_tagging import *
import multiprocessing as mp
from keras.models import load_model
from categoryapi import *


import time
vt=time.time()
#from telugu_word_embeddings import *
print("vector loading time:: ",time.time()-vt)

# =============================================================================
# from importlib import reload
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8') 
# =============================================================================


#client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
client = MongoClient('mongodb://localhost:27017')


mdb=client["way2_personalize_speed"]
user_rating_collection="rating_points_testing_users"
active_users_collection="testing_users"

# =============================================================================
# def preprocess_pool(doc):
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
#     return {"x":s,"y":doc["rating"]}
# =============================================================================


def clean_text(text):
    line = text.split(' ')
    new_doc=[]
    for w in line:
        w=re.sub('\s*\d*\s', '', w)
        if re.search('(\r\n|\n|\r|\s|^☛|☛$|\.$|^\.|^,|,$|^\'|\'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$|^#|#$|^\;|\;$|^\d|\d$|^\*|\*$|^-|-$|^\(|\)$|^\/|\/$)',w):
#                         print("wordddd",w)
                    try:
                        start = re.search('(^[☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*)',w).group()
#                             print("start",start)
                        w = w.replace(start,"")
                    except:
                        pass
                    try:
                        end = re.search('([☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*$)',w).group()
#                             print("end",end)
                        w = w.replace(end, "")
                    except:
                        pass
        else:
            pass
            #print("no special chars",w)
#             print(w)                           
        if w is not "":
            try:
#                     print("word  ",w)
                middle = re.search('[^☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*([☛\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]+).*',w).groups()[0]
#                     print("middle  ",middle)
                w = w.replace(middle," ")
                w=w.split(" ")
#                     print("split  ",w)
                if w is not "":
                    new_doc.extend(w)
            except:
                new_doc.append(w)
    return ' '.join(new_doc)


def generate_model(custid,last_post_time,avg_time_spent,total_posts):
   # custid=17967798
    #x = datetime.now()
    #today_date=str(x).split(" ")[0]
    #yesterday=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    #result_docs=mdb[user_rating_collection].find({"custid" : custid,"seen_unix_time":{'$gt':last_post_time}},{"category":1,"keywords":1,"rating":1,"seen_unix_time":1})
    result_docs=mdb[user_rating_collection].find({"custid" : custid,"seen_unix_time":{'$gt':last_post_time}},{"category":1,"post_desc":1,"keywords":1,"rating":1,"seen_unix_time":1,"max_time_spent":1,"events":1})
    docs=list(result_docs)
    print("docs length:: ",len(docs))
    #docs=mdb[user_rating_collection].find({"custid" : custid,"date" :{'$nin':["2019-03-07","2019-03-06"]}},{"category":1,"keywords":1,"rating":1})
    X=[]
    y=[]
    new_total_posts=total_posts+len(docs)
    new_last_post_time=0
    sum_time_spent=0
    for doc in docs:
        #print(doc)
        s=''
        #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
        if "post_desc" in doc and doc["post_desc"]:
            s=s+" "+category(doc["post_desc"])
            s=s+" "+doc["post_desc"]
        X.append(s)
        y.append(doc["rating"])
        new_last_post_time=doc['seen_unix_time']
        try:
                sum_time_spent=sum_time_spent+(25 if doc["max_time_spent"]>25 else doc["max_time_spent"] )
        except:
                print(doc)
# =============================================================================
#         if "events" not in doc:
#             sum_time_spent=sum_time_spent+doc["max_time_spent"]
#             new_total_posts=new_total_posts+1
# =============================================================================
        
    new_avg_time_spent=(sum_time_spent+avg_time_spent*total_posts)/new_total_posts
    print("data prepared and avg time spent is ",new_avg_time_spent)
    mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})
    if len(X)>0:
        labels=y
        
        cleaned_X=[]
        for d in X:    
            cleaned_X.append(clean_text(d))
        
        EMBEDDING_DIM=300
        MAX_SEQUENCE_LENGTH=100
        
        final_input_matrix=np.zeros((len(cleaned_X),MAX_SEQUENCE_LENGTH, EMBEDDING_DIM))        
        i=0
        for p in cleaned_X:
            awords=p.split(" ")
            #print(len(awords))
            j=0
            for w in awords:
                embedding_vector = embeddings_index.get(w)
                #print(embedding_vector[:3])
                if embedding_vector is not None:
                    # words not found in embedding index will be all-zeros.
                    final_input_matrix[i][j] = embedding_vector
                j=j+1
            i=i+1
        try:
            model=load_model("../models_olds/"+str(custid))
            model.fit(final_input_matrix, labels, epochs=10, verbose=0)
            model.save("../models_olds/"+str(custid))
            print(str(custid)+"  partial_fit")
        except:
            if len(set(y))>1:
                model = Sequential()
                model.add(Conv1D(64, 3, activation='selu',input_shape=(MAX_SEQUENCE_LENGTH,EMBEDDING_DIM)))
                model.add(GlobalMaxPooling1D())
                model.add(Dense(100, activation='selu'))
                model.add(Dense(64, activation='selu'))
                model.add(Dense(32, activation='selu'))
                model.add(Dense(11, activation='softmax'))
                model.compile(
                        optimizer=keras.optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False), 
                        loss='sparse_categorical_crossentropy', 
                        metrics=['acc'])
                print(model.summary())
                model.fit(final_input_matrix, labels, epochs=20, verbose=2)
                model.save("../models_olds/"+str(custid))
                print(str(custid)+" normal fit")
            else:
                print(str(custid)+" The number of classes has to be greater than one; got 1 class")
        #joblib.dump(vectorizer, "../models/vect_"+str(custid))
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'model_updated':1,'model_uptime':time.time(),'model_old_last_post_time':new_last_post_time,'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})
    else:
        print(str(custid)+" don't have atleast 1 flips")
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'model_updated':1,'model_uptime':time.time(),'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})

def user_model_update():
    #print(sys.argv)
    t0=time.time()
    #active_users=mdb[active_users_collection].find({'model_updated':{'$in':[None,0]}}).limit(1)
    #active_users=mdb[active_users_collection].find({'updated':int(sys.argv[1])}).limit(100)
    #active_users_df=pd.DataFrame(list(active_users))
    #if active_users.count()>0:
    if mdb[active_users_collection].count_documents({'model_updated':{'$in':[None,0]}})>0:
        print("active users are fetched for model update")
        active_users=mdb[active_users_collection].find({'model_updated':{'$in':[None,0]}}).limit(100)
        mode_gen_time={}
        #pool = mp.Pool(mp.cpu_count())
        for user in active_users:
            t3=time.time()
            last_post_time=0
            avg_time_spent=0
            total_posts=0
            if "model_last_post_time" in user and user["model_last_post_time"]:
                last_post_time=user["model_old_last_post_time"]
            if "avg_time_spent" in user and user["avg_time_spent"]:
                avg_time_spent=user["avg_time_spent"]
            if "total_posts" in user and user["total_posts"]:
                total_posts=user["total_posts"]
            generate_model(int(user["custid"]),last_post_time,avg_time_spent,total_posts)
            #pool.apply(generate_model,args=(int(user["_id"]),last_post_time))
            t4=time.time()-t3
            print(user["custid"],"  models time ",t4)
            mode_gen_time[user["custid"]]=t4
        #pool.close()
        print("models time ",mode_gen_time)
        #time.sleep(30)
        t1=time.time()-t0
        print("total time taken for 100  custids",t1)
        #user_model_update()
    else:
        mdb[active_users_collection].update_many({},{'$set':{'updated':0}})
        print("no records waiting 10 seconds to retry")
        #time.sleep(30)
        #user_model_update()
    t1=time.time()-t0
    print("total time taken ",t1)
        
    
    
    

#time.sleep(10)
user_model_update()
#generate_model(17967798)

#pool = mp.Pool(mp.cpu_count())
#results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for user in data]
#pool.close()  