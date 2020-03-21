# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from telugu_word_embeddings import *
import matplotlib.pyplot as plt
from scipy import stats
import tensorflow as tf
import seaborn as sns
from pylab import rcParams
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from keras import optimizers
from keras.models import Sequential,Model,load_model
from keras.layers import Dense,Conv1D,MaxPooling1D,GlobalAveragePooling1D,Dropout,GlobalMaxPooling1D,Input,concatenate
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras import regularizers
import keras
#from getVectors import *
from keras.utils import to_categorical
import time
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report 



data=pd.read_csv('virality_all_data.csv')

data=data[data["post_status"].isin(['published','published1','published2','published3','published4'])]
#data=data[data["post_gmt"]>1483209000]
#data=data[data["post_gmt"]>1514745000]
#data=data[data["post_gmt"]>1546281000]
data=data[data["post_gmt"]>1569868200]

data=data[data["text"].notnull()]
data = data.sort_values(by=['post_gmt'], ascending=True)

#data=data[300000:]

#y=np.array(data["target"].apply(lambda x:1 if x>0 else 0))
y=data["shares"].apply(lambda x:1 if x>0 else 0)

bins = [-1, 0, 4, 40, 200, 1000, 50000]
labels = [1,2,3,4,5,6]
y = pd.cut(data['shares'], bins=bins, labels=labels)

class_weights = class_weight.compute_class_weight('balanced',
                                                 np.unique(y),
                                                 y)


type_X=data["type"].replace({"image": 0,"fullimage": 1,"video":2})
type_X=to_categorical(type_X,3)


def topic(x):
    #print(x)
    return x.replace("మన","").strip()

data["writer_topic"]=data["writer_topic"].fillna("internal")
data["writer_topic"]=data["writer_topic"].apply(topic)
data["writer_topic"]=data["writer_topic"].replace({'internal':0, 'వరంగల్':1, 'నల్గొండ':2, 'ఖమ్మం':3, 'కరీంనగర్':4, 'మహబూబ్‌నగర్':5,'విశాఖపట్నం':6, 'గుంటూరు':7, 'ఆదిలాబాద్':7, 'రంగారెడ్డి':8, 'తూర్పు గోదావరి':9,'ప్రకాశం':10, 'విజయనగరం':11, 'కర్నూలు':12, 'మెదక్':13, 'శ్రీకాకుళం':14, 'హైదరాబాద్':15,'అనంతపురం':16, 'కృష్ణా':17, 'కడప':18, 'నెల్లూరు':19, 'నిజామాబాద్':20, 'చిత్తూరు':21,'పశ్చిమ గోదావరి':22,'మహబూబ్ నగర్':23, 'రాజకీయాలు':24, 'హెల్త్':25})
writer_topic=to_categorical(data["writer_topic"],26)

# =============================================================================
# EMBEDDING_DIM=300
# MAX_TEXT_LENGTH=60
# MAX_CAT_LENGTH=4
# 
# i=0
# new_input_matrix=np.zeros((len(data), 2*EMBEDDING_DIM))        
# 
# for index,doc in data.iterrows():
#     text=doc["text"].split(" ")
#     text_array=np.zeros((MAX_TEXT_LENGTH, EMBEDDING_DIM))
#     j=0
#     for w in text:
#         embedding_vector = embeddings_index.get(w)
#         #embedding_vector = getVectors(w,1)[0]
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             text_array[j] = embedding_vector
#             #text_array[j] = embedding_vector.decode().split(" ")
#         j=j+1
#         if j==60: break 
#     catg=doc["new_cat"].split(" ")
#     catg_array=np.zeros((MAX_CAT_LENGTH, EMBEDDING_DIM))
#     k=0
#     for w in catg:
#         embedding_vector = embeddings_index.get(w)
#         #embedding_vector = getVectors(w,1)[0]
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             catg_array[k] = embedding_vector
#             #catg_array[k] = embedding_vector.decode().split(" ")
#         k=k+1
#     text_array[text_array==0]=np.nan
#     catg_array[catg_array==0]=np.nan
#     new_input_matrix[i]=np.hstack((np.nanmean(text_array,axis=0)
#     ,np.nanmean(catg_array,axis=0)
#     #,type_X[i]
#     #,writer_topic[i]
#     ))
#     i=i+1
#     
# new_input_matrix[np.isnan(new_input_matrix)] = 0
# 
# final_sentence_matrix_train, final_sentence_matrix_test,train_type_X,test_type_X, trainY, testY = train_test_split(new_input_matrix,type_X, y, test_size=0.25, random_state=0)
# 
# mt=time.time()
# # =============================================================================
# # text_model = Sequential()
# # text_model.add(Conv1D(64, 1, activation='relu',input_shape=(2*EMBEDDING_DIM,)))
# # text_model.add(GlobalMaxPooling1D())
# # 
# # =============================================================================
# text_input=Input(shape=(2*EMBEDDING_DIM,))
# #encoded_text=text_model(text_input)
# 
# type_input=Input(shape=(3,))
# 
# merged = concatenate([text_input, type_input])
# 
# 
# merged = Dense(100, activation='relu')(merged)
# merged = Dense(64, activation='relu')(merged)
# merged = Dense(32, activation='relu')(merged)
# 
# main_output = Dense(2, activation='softmax')(merged)
# 
# model = Model(inputs=[text_input,type_input], outputs=[main_output])
# model.compile(
#         optimizer=optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, decay=0.0, amsgrad=False), 
#         #optimizer="sgd", 
#         loss='sparse_categorical_crossentropy', 
#         metrics=['acc'])
# # summarize the model
# print(model.summary())
# # fit the model
# #model.fit(final_input_matrix, labels, epochs=20, verbose=2,validation_split=0.2)
# model.fit([np.array(final_sentence_matrix_train),np.array(train_type_X)], np.array(trainY),validation_data=([np.array(final_sentence_matrix_test),np.array(test_type_X)], testY)
#            , class_weight=class_weights
#            ,epochs=10, verbose=2,batch_size=100)
# tmt=time.time()-mt
# print("time taken for train:: ",tmt)
# =============================================================================

EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(data["text"]),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in data["text"]:
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

final_cat_matrix=np.zeros((len(data["text"]),MAX_CAT_LENGTH, EMBEDDING_DIM))        
i=0
for p in data["new_cat"]:
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

# =============================================================================
# MAX_KEY_LENGTH=60
# 
# final_key_matrix=np.zeros((len(text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
# i=0
# for p in key_X:
#     awords=p.split(" ")
#     #print(len(awords))
#     j=0
#     for w in awords:
#         embedding_vector = embeddings_index.get(w)
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             final_key_matrix[i][j] = embedding_vector
#         j=j+1
#         if j==60: break
#     i=i+1
#     
# final_key_matrix[final_key_matrix==0]=np.nan
# =============================================================================


    
final_sentence_matrix=np.zeros((len(data["text"]),2, EMBEDDING_DIM))        


for p in range(len(data["text"])):
    final_sentence_matrix[p][0]=np.nanmean(final_text_matrix[p],axis=0)
    final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
    #final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
    
final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0

final_sentence_matrix_train, final_sentence_matrix_test,train_type_X,test_type_X, trainY, testY = train_test_split(final_sentence_matrix,type_X, y, test_size=0.1, random_state=0)

mt=time.time()
text_model = Sequential()
text_model.add(Conv1D(64, 1, activation='relu',input_shape=(2,EMBEDDING_DIM)))
text_model.add(GlobalMaxPooling1D())

text_input=Input(shape=(2,EMBEDDING_DIM))
encoded_text=text_model(text_input)

type_input=Input(shape=(3,))
#senti_input=Input(shape=(1,))

#merged = concatenate([encoded_text, type_input])


merged = Dense(100, activation='relu')(encoded_text)
merged = Dropout(0.5)(merged)
merged = Dense(64, activation='relu')(merged)
merged = Dropout(0.5)(merged)
merged = Dense(32, activation='relu')(merged)
#merged = Dropout(0.5)(merged)
#merged = Dense(16, activation='relu')(merged)


main_output = Dense(2, activation='softmax')(merged)

#model = Model(inputs=[text_input,type_input], outputs=[main_output])
model = Model(inputs=[text_input], outputs=[main_output])

model.compile(
        optimizer=optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, decay=0.0, amsgrad=False), 
        #optimizer="sgd", 
        loss='sparse_categorical_crossentropy', 
        metrics=['acc'])
# summarize the model
print(model.summary())
# fit the model
#model.fit(final_input_matrix, labels, epochs=20, verbose=2,validation_split=0.2)
#model.fit([np.array(final_sentence_matrix_train),np.array(train_type_X)], np.array(trainY),validation_data=([np.array(final_sentence_matrix_test),np.array(test_type_X)], testY)
model.fit([np.array(final_sentence_matrix_train)], np.array(trainY),validation_data=([np.array(final_sentence_matrix_test)], testY)
           , class_weight=class_weights
           ,epochs=100, verbose=2,batch_size=100)
tmt=time.time()-mt
print("time taken for train:: ",tmt)


loss, accuracy = model.evaluate([np.array(final_sentence_matrix_test)], np.array(testY), verbose=0)
print('Accuracy: %f' % (accuracy*100))



pred=model.predict([np.array(final_sentence_matrix_test)])
pred_labels=np.argmax(pred,axis=1)
train_results = confusion_matrix(testY, pred_labels) 
print('Confusion Matrix :')
print(train_results) 
print('Accuracy Score :',accuracy_score(testY, pred_labels)  )
print('Report : ')
print(classification_report(testY, pred_labels))
