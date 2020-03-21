from pymongo import MongoClient
import collections
import re
import sys
import numpy as np
import pandas as pd
import datetime
from categories import *
from numpy import array
import keras
from keras.models import Sequential,Model
from keras.layers import Dense,Conv1D,GlobalMaxPooling1D,Input,concatenate
#from pos_tagging import *
import multiprocessing as mp
from keras.models import load_model
from categoryapi import *
from util import *
from sentiment_analyzer import *
from vader import *

import time
vt=time.time()
#from telugu_word_embeddings import *
print("vector loading time:: ",time.time()-vt)




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
        match_string="[☛.,'\":?<>&\r\n#\s\d;*\-!()/\$]"
        unmatch_string="[^☛.,'\":?<>&\r\n#\s\d;*\-!()/\$]"
        if re.search('(^'+match_string+'|'+match_string+'*$)',w):
                    #print("wordddd",w)
                    try:
                        start = re.search('(^'+match_string+'*)',w).group()
                        #print("start",start)
                        w = w.replace(start,"")
                    except:
                        pass
                    try:
                        end = re.search('('+match_string+'*$)',w).group()
                        #print("end",end)
                        w = w.replace(end, "")
                    except:
                        pass
        else:
            pass
            #print("no special chars",w)
#             print(w)                           
        if w is not "":
            try:
                #print("word  ",w)
                middle = re.findall(unmatch_string+'*('+match_string+'+)',w)
                #print("middle  ",middle)
                for m in middle:
                    if m!='':
                        w = w.replace(m," ")
                w=w.split(" ")
                #print("split  ",w)
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
    result_docs=mdb[user_rating_collection].find({"custid" : custid,"seen_unix_time":{'$gt':last_post_time}},{"category":1,"post_desc":1,"keywords":1,"rating":1,"seen_unix_time":1,"max_time_spent":1,"events":1}).sort([("seen_unix_time",1)])
    docs=list(result_docs)
    print("docs length:: ",len(docs))
    #docs=mdb[user_rating_collection].find({"custid" : custid,"date" :{'$nin':["2019-03-07","2019-03-06"]}},{"category":1,"keywords":1,"rating":1})
# =============================================================================
#     X=[]
#     y=[]
#     new_total_posts=total_posts+len(docs)
#     new_last_post_time=0
#     sum_time_spent=0
#     for doc in docs:
#         #print(doc)
#         s=''
#         #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
#         if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
#         if "post_desc" in doc and doc["post_desc"]:
#             s=s+" "+category(doc["post_desc"])
#             s=s+" "+doc["post_desc"]
#         X.append(s)
#         y.append(doc["rating"])
#         new_last_post_time=doc['seen_unix_time']
#         try:
#                 sum_time_spent=sum_time_spent+(25 if doc["max_time_spent"]>25 else doc["max_time_spent"] )
#         except:
#                 print(doc)
# =============================================================================
    new_total_posts=total_posts+len(docs)
    new_last_post_time=0
    sum_time_spent=0            
    text_X=[]
    cat_X=[]
    key_X=[]
    y=[]
    sia= SentimentIntensityAnalyzer()
    senti_X=[]
    for doc in docs:
        #print(doc)
        s=''
        catg=''
        keys=''
        sentiment=0
        #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        if "keywords" in doc and doc["keywords"]:
            #s=s+" "+" ".join(doc["keywords"])
            keys=keys+" ".join(doc["keywords"])
        else:
            keys="Nothing"
        if "post_desc" in doc and doc["post_desc"] and doc["post_desc"]!='':
            #s=s+" "+category(doc["post_desc"])
            catg=catg+category(doc["post_desc"])
            s=s+" "+doc["post_desc"]
            sentiment=sia.polarity_scores(clean_text(doc["post_desc"]))["compound"]
        else:
            if "category" in doc and doc["category"]: catg=catg+cat[doc["category"]] if doc["category"] in cat else doc["category"]
            else:catg="Nothing"
            if "post_title" in doc and doc["post_title"] and doc["post_title"]!='':
                s=s+" "+doc["post_title"]
                sentiment=sia.polarity_scores(clean_text(doc["post_title"]))["compound"]
            
    # =============================================================================
    #         tag_list=tag(doc["post_desc"])
    #         #print(tag_list)
    #         for t in tag_list:
    #             if t["tag"].startswith('NN'):
    #                 print(t["word"])
    #                 s=s+" "+t["word"]
    #                 #s=s+" "+t["word"]+"_"+t["tag"]
    # =============================================================================
        if s=='':
            s="Nothing"
        text_X.append(s)
        cat_X.append(catg)
        key_X.append(keys)
        senti_X.append(sentiment)
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
    #mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})
    if len(text_X)>0:
        labels=y
        
# =============================================================================
#         cleaned_X=[]
#         for d in X:    
#             cleaned_X.append(clean_text(d))
#         
#         EMBEDDING_DIM=300
#         MAX_SEQUENCE_LENGTH=100
#         
#         final_input_matrix=np.zeros((len(cleaned_X),MAX_SEQUENCE_LENGTH, EMBEDDING_DIM))        
#         i=0
#         for p in cleaned_X:
#             awords=p.split(" ")
#             #print(len(awords))
#             j=0
#             for w in awords:
#                 embedding_vector = embeddings_index.get(w)
#                 #print(embedding_vector[:3])
#                 if embedding_vector is not None:
#                     # words not found in embedding index will be all-zeros.
#                     final_input_matrix[i][j] = embedding_vector
#                 j=j+1
#             i=i+1
# =============================================================================
            
        cleaned_text_X=[]
        for d in text_X:    
            cleaned_text_X.append(clean_text(d))    
        
        EMBEDDING_DIM=300
        MAX_TEXT_LENGTH=60

        final_text_matrix=np.zeros((len(cleaned_text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
        i=0
        for p in cleaned_text_X:
            awords=p.split(" ")
            #print(len(awords))
            j=0
            for w in awords:
                embedding_vector = embeddings_index.get(w)
                #print(embedding_vector[:3])
                if embedding_vector is not None:
                    # words not found in embedding index will be all-zeros.
                    final_text_matrix[i][j] = embedding_vector
                j=j+1
                if j==60: break
            i=i+1
            
        final_text_matrix[final_text_matrix==0]=np.nan
        
        
        MAX_CAT_LENGTH=4
        
        final_cat_matrix=np.zeros((len(cleaned_text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
        i=0
        for p in cat_X:
            awords=p.split(" ")
            #print(len(awords))
            j=0
            for w in awords:
                embedding_vector = embeddings_index.get(w)
                #print(embedding_vector[:3])
                if embedding_vector is not None:
                    # words not found in embedding index will be all-zeros.
                    final_cat_matrix[i][j] = embedding_vector
                j=j+1
            i=i+1
            
        final_cat_matrix[final_cat_matrix==0]=np.nan
        
        MAX_KEY_LENGTH=15
        
        final_key_matrix=np.zeros((len(cleaned_text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
        i=0
        for p in key_X:
            awords=p.split(" ")
            #print(len(awords))
            j=0
            for w in awords:
                embedding_vector = embeddings_index.get(w)
                #print(embedding_vector[:3])
                if embedding_vector is not None:
                    # words not found in embedding index will be all-zeros.
                    final_key_matrix[i][j] = embedding_vector
                j=j+1
            i=i+1
            
        final_key_matrix[final_key_matrix==0]=np.nan
        
        
            
        final_sentence_matrix=np.zeros((len(cleaned_text_X),3, EMBEDDING_DIM))        
        
        
        for p in range(len(cleaned_text_X)):
            final_sentence_matrix[p][0]=np.nanmean(final_text_matrix[p],axis=0)
            final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
            final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
            
        final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0
        try:
            model=load_model("../senti_models/"+str(custid))
            model.fit([np.array(final_sentence_matrix),np.array(senti_X)], np.array(labels), epochs=50, verbose=2)
            model.save("../senti_models/"+str(custid))
            print(str(custid)+"  partial_fit")
        except:
            if len(set(y))>1:
                text_model = Sequential()
                text_model.add(Conv1D(64, 1, activation='relu',input_shape=(3,EMBEDDING_DIM)))
                text_model.add(GlobalMaxPooling1D())
                
                text_input=Input(shape=(3,EMBEDDING_DIM))
                encoded_text=text_model(text_input)
                
                senti_input=Input(shape=(1,))
                
                merged = concatenate([encoded_text, senti_input])
                
                
                merged = Dense(100, activation='relu')(merged)
                merged = Dense(64, activation='relu')(merged)
                merged = Dense(32, activation='relu')(merged)
                
                main_output = Dense(11, activation='softmax')(merged)
                
                model = Model(inputs=[text_input, senti_input], outputs=[main_output])
                model.compile(
                        optimizer=keras.optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False), 
                        #optimizer="sgd", 
                        loss='sparse_categorical_crossentropy', 
                        metrics=['acc'])
                # summarize the model
                print(model.summary())
                # fit the model
                model.fit([np.array(final_sentence_matrix),np.array(senti_X)], np.array(labels), epochs=50, verbose=2)
                model.save("../senti_models/"+str(custid))
                print(str(custid)+" normal fit")
            else:
                print(str(custid)+" The number of classes has to be greater than one; got 1 class")
        #joblib.dump(vectorizer, "../models/vect_"+str(custid))
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'model_senti_updated':1,'model_senti_uptime':time.time(),'model_senti_last_post_time':new_last_post_time,'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})
    else:
        print(str(custid)+" don't have atleast 1 flips")
        print(custid," last post time",new_last_post_time)
        mdb[active_users_collection].update_one({"custid" : custid},{'$set':{'model_senti_updated':1,'model_senti_uptime':time.time(),'avg_time_spent':new_avg_time_spent,"total_posts":new_total_posts}})

def user_model_update():
    #print(sys.argv)
    t0=time.time()
    #active_users=mdb[active_users_collection].find({'model_updated':{'$in':[None,0]}}).limit(1)
    #active_users=mdb[active_users_collection].find({'updated':int(sys.argv[1])}).limit(100)
    #active_users_df=pd.DataFrame(list(active_users))
    #if active_users.count()>0:
    if mdb[active_users_collection].count_documents({'model_senti_updated':{'$in':[None,0]}})>0:
        print("active users are fetched for model update")
        active_users=mdb[active_users_collection].find({'model_senti_updated':{'$in':[None,0]}}).limit(100)
        mode_gen_time={}
        #pool = mp.Pool(mp.cpu_count())
        for user in active_users:
            t3=time.time()
            last_post_time=0
            avg_time_spent=0
            total_posts=0
            if "model_senti_last_post_time" in user and user["model_senti_last_post_time"]:
                last_post_time=user["model_senti_last_post_time"]
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
        mdb[active_users_collection].update_many({},{'$set':{'model_senti_updated':0}})
        print("no records waiting 10 seconds to retry")
        #time.sleep(30)
        user_model_update()
    t1=time.time()-t0
    print("total time taken ",t1)
        
    
    
    

#time.sleep(10)
user_model_update()
#generate_model(17967798)

#pool = mp.Pool(mp.cpu_count())
#results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for user in data]
#pool.close()  