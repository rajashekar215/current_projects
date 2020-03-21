# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import re
from telugu_word_embeddings import *
import time
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential,Model
from keras.layers import Dense,Conv1D,MaxPooling1D,GlobalAveragePooling1D,Dropout,GlobalMaxPooling1D,Input,concatenate
from keras import optimizers
from sklearn.model_selection import train_test_split
from keras.models import load_model
#from getVectors import *
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report 




total_data=pd.read_csv("virality_data_updated.csv")

#total_data=total_data[total_data["post_gmt"]>1483209000]

#total_data=total_data[total_data["text"].notnull()]



total_data = total_data.sort_values(by=['post_gmt'], ascending=True)

train_total_data=total_data[total_data["shares"]>0]

train_total_data=train_total_data[:1000]


y=train_total_data["shares"]


#text_X=train_total_data["text"]
#cat_X=train_total_data["new_cat"]
#key_X=train_total_data["keys"]
#senti_X=train_total_data["sentiment"]
type_X=train_total_data["type"]
#y=train_total_data["target"].apply(lambda x:1 if x>0 else 0)


EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60
MAX_CAT_LENGTH=4

#final_text_matrix=np.zeros((len(data["text"]),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
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

new_input_matrix=np.zeros((len(train_total_data), 2*EMBEDDING_DIM))        

for index,doc in train_total_data.iterrows():
    text=doc["text"].split(" ")
    text_array=np.zeros((MAX_TEXT_LENGTH, EMBEDDING_DIM))
    j=0
    for w in text:
        embedding_vector = embeddings_index.get(w)
        #embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            text_array[j] = embedding_vector
            #text_array[j] = embedding_vector.decode().split(" ")
        j=j+1
        if j==60: break 
    catg=doc["new_cat"].split(" ")
    catg_array=np.zeros((MAX_CAT_LENGTH, EMBEDDING_DIM))
    k=0
    for w in catg:
        embedding_vector = embeddings_index.get(w)
        #embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            catg_array[k] = embedding_vector
            #catg_array[k] = embedding_vector.decode().split(" ")
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

final_sentence_matrix_train, final_sentence_matrix_test, trainY, testY = train_test_split(new_input_matrix, y, test_size=0.25, random_state=0)


tree = DecisionTreeRegressor(criterion='mse',     # Initialize and fit regressor
                             max_depth=3)         
tree.fit(final_sentence_matrix_train, trainY)


test_predY=tree.predict(np.array(final_sentence_matrix_test))

err=np.array(testY) -test_predY.ravel()
#mse = np.mean(np.power(testY - test_predY.ravel(), 2), axis=0)
error_df = pd.DataFrame({'reconstruction_error': err,
                        'true_values': testY,
                        'pred_values': test_predY.ravel()
                        })
error_df.describe()                          


tp=test_predY[:5]
ap=testY[:5]

a=[1 if r >0 else 0 for r in testY]
b=[1 if r >0 else 0 for r in np.floor(test_predY.ravel())]


train_results = confusion_matrix(a, b) 
print('Confusion Matrix :')
print(train_results) 
print('Accuracy Score :',accuracy_score(a, b)  )
print('Report : ')
print(classification_report(a, b))



