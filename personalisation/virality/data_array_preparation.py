# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy import stats
import tensorflow as tf
import seaborn as sns
from pylab import rcParams
from sklearn.model_selection import train_test_split
from keras.models import Model, load_model
from keras.layers import Input, Dense, Conv1D, MaxPooling1D, UpSampling1D
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras import regularizers
import keras
#from getVectors import *
from keras.utils import to_categorical
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import requests
import re
import itertools

#from os import sched_getaffinity as aff
#aff(0)

def getProxy():
   #proxyList=[]
   response = requests.get(
       "https://www.proxy-list.download/api/v1/get?type=https&anon=elite&country=us")
   print("got response from proxy server")
   proxy = (response.text)
   proxy_list = proxy.split('\r\n')
   print(proxy_list)
   proxyList = []
   for x in range(1, len(proxy_list)):
       ipPattern = re.compile(
           "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$")
       if re.match(ipPattern, proxy_list[x]):
           proxyList.append("https://"+proxy_list[x])
           #proxyList.append(proxy_list[x])
   return proxyList

proxyList=getProxy()

def proxy():
    response = requests.get(
        "https://www.proxy-list.download/api/v1/get?type=http&a}non=elite&country=in")
    proxy = (response.text)
    proxt_list = proxy.split('\r\n')
    proxy_dict = dict(itertools.zip_longest(
        *[iter(proxt_list)] * 2, fillvalue=""))
    return proxy_dict

proxyList=proxy()


data=pd.read_csv('virality_data_updated.csv')

pytrends = TrendReq()

#pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1)

pytrends = TrendReq(proxies=proxyList)

def getTrend(x):
    keys=x["keys"].split(" ")
    print(keys)
    today=x["post_date"]
    yday=datetime.strftime(datetime.strptime(today, "%Y-%m-%d") - timedelta(1), '%Y-%m-%d')
    dyday=datetime.strftime(datetime.strptime(today, "%Y-%m-%d") - timedelta(2), '%Y-%m-%d')
    print(today,yday,dyday)
    pytrends.build_payload(kw_list=keys[:1],geo='IN',timeframe=today+" "+yday+" "+dyday)
    trend_df=pytrends.interest_over_time()
    print(trend_df)
    
data[:1].apply(getTrend,axis=1) 


def getNER(x):
    keys=x["keys"].split(" ")
    print(keys)
    today=x["post_date"]
    yday=datetime.strftime(datetime.strptime(today, "%Y-%m-%d") - timedelta(1), '%Y-%m-%d')
    dyday=datetime.strftime(datetime.strptime(today, "%Y-%m-%d") - timedelta(2), '%Y-%m-%d')
    print(today,yday,dyday)
    pytrends.build_payload(kw_list=keys[:1],geo='IN',timeframe=today+" "+yday+" "+dyday)
    trend_df=pytrends.interest_over_time()
    print(trend_df)
    
data[:1].apply(getNER,axis=1)    
    



data=data[data["post_status"].isin(['published','published1','published2','published3','published4'])]
#data=data[data["post_gmt"]>1483209000]
#data=data[data["post_gmt"]>1514745000]
data=data[data["post_gmt"]>1546281000]
#data=data[data["post_gmt"]>1570818600]

#data=data[data["text"].notnull()]
data = data.sort_values(by=['post_gmt'], ascending=True)

#data=data[300000:]
#data['target']=data['target'].apply(lambda x:1 if x>0 else 0)

# =============================================================================
# count_classes=pd.value_counts(data['target'],sort=True)
# count_classes.plot(kind = 'bar', rot=0)
# =============================================================================

# =============================================================================
# frauds = data[data.target == 1]
# normal = data[data.target == 0]
# =============================================================================

# =============================================================================
# from sklearn.preprocessing import StandardScaler
# dat = data.drop(['Time'], axis=1)
# dat['Amount'] = StandardScaler().fit_transform(data['Amount'].values.reshape(-1, 1))
# =============================================================================

#train_total_data=data[300000:]

#text_X=train_total_data["text"]
#cat_X=train_total_data["category"]
#key_X=train_total_data["keys"]
#senti_X=train_total_data["sentiment"]
#type_X=train_total_data["type"]
#y=np.array(data["target"].apply(lambda x:1 if x>0 else 0))
y=np.array(data["shares"].apply(lambda x:1 if x>0 else 0))


type_X=data["type"].replace({"image": 0,"fullimage": 1,"video":2})
type_X=to_categorical(type_X,3)


def topic(x):
    #print(x)
    return x.replace("మన","").strip()

data["writer_topic"]=data["writer_topic"].fillna("internal")
data["writer_topic"]=data["writer_topic"].apply(topic)
data["writer_topic"]=data["writer_topic"].replace({'internal':0, 'వరంగల్':1, 'నల్గొండ':2, 'ఖమ్మం':3, 'కరీంనగర్':4, 'మహబూబ్‌నగర్':5,'విశాఖపట్నం':6, 'గుంటూరు':7, 'ఆదిలాబాద్':7, 'రంగారెడ్డి':8, 'తూర్పు గోదావరి':9,'ప్రకాశం':10, 'విజయనగరం':11, 'కర్నూలు':12, 'మెదక్':13, 'శ్రీకాకుళం':14, 'హైదరాబాద్':15,'అనంతపురం':16, 'కృష్ణా':17, 'కడప':18, 'నెల్లూరు':19, 'నిజామాబాద్':20, 'చిత్తూరు':21,'పశ్చిమ గోదావరి':22,'మహబూబ్ నగర్':23, 'రాజకీయాలు':24, 'హెల్త్':25})
writer_topic=to_categorical(data["writer_topic"],26)

EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60
MAX_CAT_LENGTH=4

final_text_matrix=np.zeros((len(data["text"]),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0

# =============================================================================
# for k in range(len(key_X)):
#     p=key_X[k]
#     awords=""
#     if type(p)==str and len(p.split(" "))>=10:
#         awords=p.split(" ")
#     else:
#         awords=text_X[k].split(" ")
#     
#     awords=p.split(" ")
#     #print(len(awords))
#     j=0
#     for w in awords:
#         embedding_vector = embeddings_index.get(w)
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             final_text_matrix[i][j] = embedding_vector
#         j=j+1
#         if j==60: break
#     i=i+1
# =============================================================================

new_input_matrix=np.zeros((len(data), 2*EMBEDDING_DIM))        

for index,doc in data.iterrows():
    text=doc["text"].split(" ")
    text_array=np.zeros((MAX_TEXT_LENGTH, EMBEDDING_DIM))
    j=0
    for w in text:
        embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            text_array[j] = embedding_vector.decode().split(" ")
        j=j+1
        if j==60: break 
    catg=doc["new_cat"].split(" ")
    catg_array=np.zeros((MAX_CAT_LENGTH, EMBEDDING_DIM))
    k=0
    for w in catg:
        embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            catg_array[k] = embedding_vector.decode().split(" ")
        k=k+1
    text_array[text_array==0]=np.nan
    catg_array[catg_array==0]=np.nan
    new_input_matrix[i]=np.hstack((np.nanmean(text_array,axis=0)
    ,np.nanmean(catg_array,axis=0)
    #,type_X[i]
    #,writer_topic[i]
    ))
    i=i+1
    
new_input_matrix[np.isnan(new_input_matrix)] = 0
np.savetxt('input.txt',new_input_matrix)   

           


# =============================================================================
# 
# for p in data["text"]:
#     awords=p.split(" ")
#     #print(len(awords))
#     j=0
#     for w in awords:
#         embedding_vector = getVectors(w,1)[0]
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             final_text_matrix[i][j] = embedding_vector.decode().split(" ")
#         j=j+1
#         if j==60: break
#     i=i+1
#     
# final_text_matrix[final_text_matrix==0]=np.nan
# 
# 
# MAX_CAT_LENGTH=4
# 
# final_cat_matrix=np.zeros((len(data["text"]),MAX_CAT_LENGTH, EMBEDDING_DIM))        
# i=0
# for p in data["new_cat"]:
#     awords=p.split(" ")
#     #print(len(awords))
#     j=0
#     for w in awords:
#         embedding_vector = getVectors(w,1)[0]
#         #print(embedding_vector[:3])
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             final_cat_matrix[i][j] = embedding_vector.decode().split(" ")
#         j=j+1
#     i=i+1
#     
# final_cat_matrix[final_cat_matrix==0]=np.nan
# 
# 
# # =============================================================================
# # MAX_KEY_LENGTH=60
# # 
# # final_key_matrix=np.zeros((len(text_X),MAX_KEY_LENGTH, EMBEDDING_DIM))        
# # i=0
# # for p in key_X:
# #     awords=p.split(" ")
# #     #print(len(awords))
# #     j=0
# #     for w in awords:
# #         embedding_vector = embeddings_index.get(w)
# #         #print(embedding_vector[:3])
# #         if embedding_vector is not None:
# #             # words not found in embedding index will be all-zeros.
# #             final_key_matrix[i][j] = embedding_vector
# #         j=j+1
# #         if j==60: break
# #     i=i+1
# #     
# # final_key_matrix[final_key_matrix==0]=np.nan
# # =============================================================================
# 
# new_input_matrix=np.hstack((np.nanmean(final_text_matrix,axis=1),np.nanmean(final_cat_matrix,axis=1)))
#     
# new_input_matrix[np.isnan(new_input_matrix)] = 0
# 
# 
# 
# 
# np.savetxt('input.txt',new_input_matrix)
# np.savetxt('target.txt',y)
# 
# =============================================================================
#y = np.loadtxt('text.txt')


final_sentence_matrix_train, final_sentence_matrix_test, trainY, testY = train_test_split(new_input_matrix, y, test_size=0.25, random_state=0)

# =============================================================================
# final_sentence_matrix=np.zeros((len(text_X),2, EMBEDDING_DIM))        
# 
# 
# for p in range(len(text_X)):
#     final_sentence_matrix[p][0]=np.nanmean(final_text_matrix[p],axis=0)
#     final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
#     #final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
#     
# final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0
# 
# final_sentence_matrix_train, final_sentence_matrix_test, trainY, testY = train_test_split(final_sentence_matrix, y, test_size=0.25, random_state=0)
# 
# =============================================================================
encoder_input=[]
for i in range(len(trainY)):
    #print(i,trainY[i])
    if trainY[i]==1:
        encoder_input.append(final_sentence_matrix_train[i])
        
encoder_input=np.array(encoder_input)
        
        
# =============================================================================
# X_train, X_test = train_test_split(data, test_size=0.2, random_state=0)
# X_train = X_train[X_train.target == 0]
# X_train = X_train.drop(['target'], axis=1)
# y_test = X_test['target']
# X_test = X_test.drop(['target'], axis=1)
# X_train = X_train.values
# X_test = X_test.values
# X_train.shape
# =============================================================================
 
input_dim = encoder_input.shape[1]
encoding_dim = 300
       
input_layer=Input(shape=(input_dim,))
encoder=Dense(encoding_dim,activation="selu" 
                ,activity_regularizer=regularizers.l1(10e-5)
                )(input_layer)
encoder=keras.layers.Dropout(0.1)(encoder)
encoder=Dense(int(encoding_dim/2),activation="selu" 
                ,activity_regularizer=regularizers.l1(10e-5)
                )(encoder)
encoder=keras.layers.Dropout(0.2)(encoder)
encoder=Dense(int(encoding_dim/4),activation="selu" 
                ,activity_regularizer=regularizers.l1(10e-5)
                )(encoder)
encoder=keras.layers.Dropout(0.2)(encoder)
decoder = Dense(int(encoding_dim / 4), activation='selu')(encoder)
decoder = Dense(int(encoding_dim / 2), activation='selu')(decoder)
decoder = Dense(input_dim, activation='selu')(decoder)
autoencoder = Model(inputs=input_layer, outputs=decoder)

nb_epoch = 100
batch_size = 128
adam=keras.optimizers.Adam(lr=0.001)
autoencoder.compile(optimizer=adam, 
                    loss='mean_squared_error', 
                    metrics=['accuracy'])
autoencoder.summary()

autoencoder.fit(encoder_input, encoder_input,
                    epochs=nb_epoch,
                    batch_size=batch_size,
                    shuffle=True,
                    validation_data=(final_sentence_matrix_test, final_sentence_matrix_test),
                    verbose=1)
                          
                          
predictions = autoencoder.predict(final_sentence_matrix_test)
mse = np.mean(np.power(final_sentence_matrix_test - predictions, 2), axis=1)
error_df = pd.DataFrame({'reconstruction_error': mse,
                        'true_class': testY})
error_df.describe()                          


threshold = 0.0005
groups = error_df.groupby('true_class')
fig, ax = plt.subplots()

for name, group in groups:
    ax.plot(group.index, group.reconstruction_error, marker='o', ms=3.5, linestyle='',
            label= "Fraud" if name == 1 else "Normal")
ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
ax.legend()
plt.title("Reconstruction error for different classes")
plt.ylabel("Reconstruction error")
plt.xlabel("Data point index")
plt.show();

from sklearn.metrics import (confusion_matrix, precision_recall_curve, auc,
                             roc_curve, recall_score, classification_report, f1_score,
                             precision_recall_fscore_support,accuracy_score)
y_pred = [1 if e > threshold else 0 for e in error_df.reconstruction_error.values]
conf_matrix = confusion_matrix(error_df.true_class, y_pred)
#plt.figure(figsize=(12, 12))
sns.heatmap(conf_matrix, xticklabels="x", yticklabels="y", annot=True, fmt="d");
plt.title("Confusion matrix")
plt.ylabel('True class')
plt.xlabel('Predicted class')
plt.show()      

print('Accuracy Score :',accuracy_score(error_df.true_class, y_pred)  )
print('Report : ')
print(classification_report(error_df.true_class, y_pred))
