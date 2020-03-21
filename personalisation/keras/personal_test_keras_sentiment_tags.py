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
from keras.models import Sequential,Model
from keras.layers import Dense,Conv1D,Conv2D,MaxPooling1D,MaxPooling2D,GlobalAveragePooling1D,Dropout,GlobalMaxPooling1D,Input,concatenate
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
#from pos_tagging import *
import multiprocessing as mp
from keras.models import load_model
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 
#from telugu_word_embeddings import *
from categoryapi import *
from vadersentiment.vader import *
from indic_tagger.pipeline import *


#telugu_stop_words=["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి"]

t0=time.time()
#client = MongoClient('mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2')
client = MongoClient('mongodb://localhost:27017')
#db=client.way2
mdb=client["way2_personalize_speed"]







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


def count_words(count_dict, text):
    '''Count the number of occurrences of each word in a set of text'''
    for sentence in text:
        for word in sentence.split():
            if word not in count_dict:
                count_dict[word] = 1
            else:
                count_dict[word] += 1
                
                
                
custid=22172222
documents=mdb.rating_points_testing_users.find({"custid" : custid,"date" :{"$nin":["2019-10-03","2019-10-04"]}},{"category":1,"keywords":1,"post_desc":1,"rating":1})
#documents=mdb.rating_points_testing_users.find({"custid" : custid,"$and":[{"date" :{"$gt":"2019-08-15"}},{"date" :{"$nin":["2019-08-30"]}}]},{"category":1,"keywords":1,"post_desc":1,"rating":1})
docs=list(documents)



# =============================================================================
# cf=open("misscat","w+")
# for doc in docs:
#     #print(doc["post_desc"])
#     if "post_desc" in doc and doc["post_desc"] and doc["post_desc"]!='' and category(doc["post_desc"])==' ':
#         cf.write(doc["post_desc"])
#         #print(doc["post_desc"])
#         #print("-------------------------------------------------------------")
#     else:
#         pass
#         #print(c)
# =============================================================================


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
# =============================================================================
#     if "keywords" in doc and doc["keywords"]:
#         #s=s+" "+" ".join(doc["keywords"])
#         keys=keys+" ".join(doc["keywords"])
#     else:
#         keys="Nothing"
# =============================================================================
    if "post_desc" in doc and doc["post_desc"] and doc["post_desc"]!='':
        #s=s+" "+category(doc["post_desc"])
        catg=catg+category(doc["post_desc"])
        s=s+" "+doc["post_desc"]
        sentiment=sia.polarity_scores(clean_text(doc["post_desc"]))["compound"]
        tags=getTaggers(doc["post_desc"],"te")
        if 'NN' in tags and len(tags['NN'])>0:
            keys=keys+' '.join(tags['NN'])
        if 'NNP' in tags and len(tags['NNP'])>0:
            keys=keys+" "+' '.join(tags['NNP'])
        if 'VM' in tags and len(tags['VM'])>0:
            keys=keys+" "+' '.join(tags['VM'])
    else:
        if "category" in doc and doc["category"]: catg=catg+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        else:catg="Nothing"
        if "post_title" in doc and doc["post_title"] and doc["post_title"]!='':
                s=s+" "+doc["post_title"]
                sentiment=sia.polarity_scores(clean_text(doc["post_title"]))["compound"]
                tags=getTaggers(doc["post_title"],"te")
                if 'NN' in tags and len(tags['NN'])>0:
                    keys=keys+' '.join(tags['NN'])
                if 'NNP' in tags and len(tags['NNP'])>0:
                    keys=keys+" "+' '.join(tags['NNP'])
                if 'VM' in tags and len(tags['VM'])>0:
                    keys=keys+" "+' '.join(tags['VM'])
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
    if keys=='':
        keys="Nothing"
    text_X.append(s)
    cat_X.append(catg)
    key_X.append(keys)
    senti_X.append(sentiment)
    y.append(doc["rating"])

cleaned_text_X=[]
for d in text_X:    
    cleaned_text_X.append(clean_text(d))
    
cleaned_key_X=[]
for c in key_X:    
    cleaned_key_X.append(clean_text(c))

word_counts = {}

count_words(word_counts, cleaned_text_X)

print("Size of Vocabulary:", len(word_counts))

# =============================================================================
# embeddings_index = {}
# with open('telugu.vec', encoding='utf-8', newline='\n', errors='ignore') as f:
#     for line in f:
#         values = line.split(' ')
#         word = values[0]
#         embedding = np.asarray(values[1:], dtype='float32')
#         embeddings_index[word] = embedding
# =============================================================================
        
        

print('Word embeddings:', len(embeddings_index))

# =============================================================================
# with open("fasttext_telugu_embeddings_matrix.py", "w") as write_file:
# 		write_file.write("embeddings_index="+str(embeddings_index)+"\n")
#             
# =============================================================================
missing_words = 0
threshold = 20
m_words=[]

for word, count in word_counts.items():
    if count > threshold:
        if word not in embeddings_index:
            missing_words += 1
            m_words.append(word)
            
missing_ratio = round(missing_words/len(word_counts),4)*100
            
print("Number of words missing from CN:", missing_words)
print("words missing from CN:", m_words)
print("Percent of words that are missing from vocabulary: {}%".format(missing_ratio))

EMBEDDING_DIM=300

embedding_matrix = np.zeros((len(word_counts) + 1, EMBEDDING_DIM))
for word, i in word_counts.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector
        

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

MAX_KEY_LENGTH=60

final_key_matrix=np.zeros((len(cleaned_text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
i=0
for p in cleaned_key_X:
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
        if j==60: break
    i=i+1
    
final_key_matrix[final_key_matrix==0]=np.nan


    
final_sentence_matrix=np.zeros((len(cleaned_text_X),3, EMBEDDING_DIM))        


for p in range(len(cleaned_text_X)):
    final_sentence_matrix[p][0]=np.nanmean(final_text_matrix[p],axis=0)
    final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
    final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
    
final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0
# =============================================================================
# from keras.utils import to_categorical        
# labels=to_categorical(y)
# =============================================================================
labels=y
# =============================================================================
# labels=np.expand_dims(y,2)
# labels=labels.reshape(labels.shape[0],labels.shape[1],1)
# =============================================================================

t1=time.time()-t0
print("time taken for preprocess",t1)

#array_new = np.expand_dims(final_sentence_matrix,2)


mt=time.time()
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
#model.fit(final_input_matrix, labels, epochs=20, verbose=2,validation_split=0.2)
model.fit([np.array(final_sentence_matrix),np.array(senti_X)], np.array(labels), epochs=50, verbose=2)
tmt=time.time()-mt
print("time taken for train:: ",tmt)

et=time.time()
# evaluate the model
loss, accuracy = model.evaluate([np.array(final_sentence_matrix),np.array(senti_X)], np.array(labels), verbose=0)
print('Accuracy: %f' % (accuracy*100))
tet=time.time()-et
print("time taken for evaluation:: ",tet)
#model.save(str(custid))


pred=model.predict([np.array(final_sentence_matrix),np.array(senti_X)])
pred_labels=np.argmax(pred,axis=1)
train_results = confusion_matrix(labels, pred_labels) 
print('Confusion Matrix :')
print(train_results) 
print('Accuracy Score :',accuracy_score(labels, pred_labels)  )
print('Report : ')
print(classification_report(labels, pred_labels))


#del model
#custid=22172222
t4=time.time()
tlist=mdb.rating_points_testing_users.find({"custid" : custid,"date":{"$in":["2019-10-03","2019-10-04"]}},{"category":1,"keywords":1,"post_desc":1,"rating":1})
test_docs=list(tlist)
# =============================================================================
# test_docs=[
# # =============================================================================
# #         {
# #     "_id" : "5d4ec5d6ca0207b50b387752",
# #     "custid" : 21887067,
# #     "postid" : 2315947,
# #     "date" : "2019-08-06",
# #     "keywords" : [ 
# #         "bat", 
# #         "flight"
# #     ],
# #     "category" : "రాజకీయాలు",
# #     "post_desc" : '''అమెరికాలోని నార్త్ కరోలినా నుంచి న్యూజెర్సీకి వెళుతున్న స్పిరిట్  
# #     ఎయిర్ ‌లైన్స్‌లో చక్కర్లు కొడుతున్న గబ్బిలాన్ని చూసి ప్రయాణికులు 
# #     ఆందోళనకు గురయ్యారు. తమపై ఎక్కడ వాలుతుందో అనే భయంతో 
# #     కొందరు వాష్ రూమ్‌లోకి దూరారు. ప్రస్తుతం ఈ వీడియో సోషల్ మీడియాలో వైరల్ అవుతోంది.''',
# #     "rating" : 5
# # },
# # =============================================================================
#     {
#     "_id" :"5d4ec5eeca0207b50b38785e",
#     "custid" : 21887067,
#     "postid" : 2325866,
#     "date" : "2019-08-07",
#     "keywords" : [ 
#              
#        
#          
#        
#     ],
#     "category" : "రాజకీయాలు",
#     "post_desc" : """ ఎమిరేట్స్‌ సంస్థ తన అధికారిక
#     ట్విటర్‌ ఖాతాలో దీన్ని పోస్ట్ చేసింది. పోస్ట్‌ చేసిన కొద్దిసేపటికే దీనిని 2.8 లక్షల మంది వీక్షించారు. """,
#     "rating" : 5
# }]
# =============================================================================

test_text_X=[]
test_cat_X=[]
test_key_X=[]
test_senti_X=[]
test_y=[]
for doc in test_docs:
    #print(doc)
    s=''
    catg=''
    keys=''
    sentiment=0
    #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
# =============================================================================
#     if "keywords" in doc and doc["keywords"]:
#         #s=s+" "+" ".join(doc["keywords"])
#         keys=keys+" ".join(doc["keywords"])
#     else:
#         keys="Nothing"
# =============================================================================
    if "post_desc" in doc and doc["post_desc"] and doc["post_desc"]!='':
        #s=s+" "+category(doc["post_desc"])
        catg=catg+category(doc["post_desc"])
        s=s+" "+doc["post_desc"]
        sentiment=sia.polarity_scores(clean_text(doc["post_desc"]))["compound"]
        tags=getTaggers(doc["post_desc"],"te")
        if 'NN' in tags and len(tags['NN'])>0:
            keys=keys+' '.join(tags['NN'])
        if 'NNP' in tags and len(tags['NNP'])>0:
            keys=keys+" "+' '.join(tags['NNP'])
        if 'VM' in tags and len(tags['VM'])>0:
            keys=keys+" "+' '.join(tags['VM'])
    else:
        if "category" in doc and doc["category"]: catg=catg+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        else:catg="Nothing"
        if "post_title" in doc and doc["post_title"] and doc["post_title"]!='':
                s=s+" "+doc["post_title"]
                sentiment=sia.polarity_scores(clean_text(doc["post_title"]))["compound"]
                tags=getTaggers(doc["post_title"],"te")
                if 'NN' in tags and len(tags['NN'])>0:
                    keys=keys+' '.join(tags['NN'])
                if 'NNP' in tags and len(tags['NNP'])>0:
                    keys=keys+" "+' '.join(tags['NNP'])
                if 'VM' in tags and len(tags['VM'])>0:
                    keys=keys+" "+' '.join(tags['VM'])
        
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
    if keys=='':
        keys="Nothing"
    test_text_X.append(s)
    test_cat_X.append(catg)
    test_key_X.append(keys)
    test_senti_X.append(sentiment)
    test_y.append(doc["rating"])

test_cleaned_text_X=[]
for d in test_text_X:    
    test_cleaned_text_X.append(clean_text(d))



test_cleaned_key_X=[]
for d in test_key_X:    
    test_cleaned_key_X.append(clean_text(d))


# =============================================================================
# test_x=[]
# test_y=[]
# 
# for doc in test_docs:
#     #print(doc)
#     s=''
#     #if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
#     if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
#     if "post_desc" in doc and doc["post_desc"] and doc["post_desc"]!='':
#         s=s+" "+category(doc["post_desc"])
#         s=s+" "+doc["post_desc"]
# # =============================================================================
# #         tag_list=tag(doc["post_desc"])
# #         #print(tag_list)
# #         for t in tag_list:
# #             if t["tag"].startswith('NN'):
# #                 print(t["word"])
# #                 s=s+" "+t["word"]
# #                 #s=s+" "+t["word"]+"_"+t["tag"]
# # =============================================================================
#     if s=='':
#         s="Nothing"
#     test_x.append(s)
#     test_y.append(doc["rating"])
# 
# 
# #model1=load_model(str(custid))
# 
# 
# cleaned_test_X=[]
# for d in test_x:    
#     cleaned_test_X.append(clean_text(d))
# =============================================================================

test_word_counts = {}

count_words(test_word_counts, test_cleaned_text_X)

print("Size of Vocabulary:", len(test_word_counts))


test_missing_words = 0
threshold = 20
test_m_words=[]

for word, count in test_word_counts.items():
    if count > threshold:
        if word not in embeddings_index:
            test_missing_words += 1
            test_m_words.append(word)
            
test_missing_ratio = round(test_missing_words/len(test_word_counts),4)*100
            
print("Number of words missing from CN:", test_missing_words)
print("words missing from CN:", test_m_words)
print("Percent of words that are missing from vocabulary: {}%".format(test_missing_ratio))

# =============================================================================
# final_input_matrix_test=np.zeros((len(cleaned_test_X),MAX_SEQUENCE_LENGTH, EMBEDDING_DIM))        
# i=0
# for p in cleaned_test_X:
#     awords=p.split(" ")
#     j=0
#     for w in awords:
#         embedding_vector = embeddings_index.get(w)
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             final_input_matrix_test[i][j] = embedding_vector
#         j=j+1
#     i=i+1
# 
# final_input_matrix_test[final_input_matrix_test==0]=np.nan
#     
# final_sentence_matrix_test=np.zeros((len(cleaned_test_X), EMBEDDING_DIM))        
# 
# 
# for p in range(final_input_matrix_test.shape[0]):
#     final_sentence_matrix_test[p]=np.nanmean(final_input_matrix_test[p],axis=0)
# 
# final_sentence_matrix_test[np.isnan(final_sentence_matrix_test)] = 0
# =============================================================================



MAX_TEXT_LENGTH=60

test_final_text_matrix=np.zeros((len(test_cleaned_text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in test_cleaned_text_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            test_final_text_matrix[i][j] = embedding_vector
        j=j+1
        if j==60: break
    i=i+1
    
test_final_text_matrix[test_final_text_matrix==0]=np.nan


MAX_CAT_LENGTH=4

test_final_cat_matrix=np.zeros((len(test_cleaned_text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
i=0
for p in test_cat_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            test_final_cat_matrix[i][j] = embedding_vector
        j=j+1
    i=i+1
    
test_final_cat_matrix[test_final_cat_matrix==0]=np.nan

MAX_KEY_LENGTH=60

test_final_key_matrix=np.zeros((len(test_cleaned_text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
i=0
for p in test_cleaned_key_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            test_final_key_matrix[i][j] = embedding_vector
        j=j+1
        if j==60: break
    i=i+1
    
test_final_key_matrix[test_final_key_matrix==0]=np.nan


    
test_final_sentence_matrix=np.zeros((len(test_cleaned_text_X),3, EMBEDDING_DIM))        


for p in range(len(test_cleaned_text_X)):
    test_final_sentence_matrix[p][0]=np.nanmean(test_final_text_matrix[p],axis=0)
    test_final_sentence_matrix[p][1]=np.nanmean(test_final_cat_matrix[p],axis=0)
    test_final_sentence_matrix[p][2]=np.nanmean(test_final_key_matrix[p],axis=0)
    
test_final_sentence_matrix[np.isnan(test_final_sentence_matrix)] = 0
#model1=load_model(str(custid))
#final_sentence_matrix_test=np.expand_dims(final_sentence_matrix_test,2)    
#model=load_model("../models/"+str(custid))
#pred_y=model.predict_classes(test_final_sentence_matrix)

pred=model.predict([np.array(test_final_sentence_matrix),np.array(test_senti_X)])
pred_y=np.argmax(pred,axis=1)
t5=time.time()-t4
print("time taken for test:: ",t5)



results = confusion_matrix(test_y, pred_y) 
print('Confusion Matrix :')
print(results) 
print('Accuracy Score :',accuracy_score(test_y, pred_y) )
print('Report : ')
print(classification_report(test_y, pred_y) )



for i in range(len(pred_y)):
    if pred_y[i]==1:
        print(test_docs[i])








