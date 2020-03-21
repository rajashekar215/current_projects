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
from getVectors import *



total_data=pd.read_csv("virality_data_updated.csv")

#total_data=total_data[total_data["post_gmt"]>1483209000]

#total_data=total_data[total_data["text"].notnull()]



total_data = total_data.sort_values(by=['post_gmt'], ascending=True)

train_total_data=total_data[total_data["shares"]>0]

train_total_data=train_total_data[:1000]


y=train_total_data["shares"]


text_X=train_total_data["text"]
cat_X=train_total_data["new_cat"]
#key_X=train_total_data["keys"]
#senti_X=train_total_data["sentiment"]
type_X=train_total_data["type"]
#y=train_total_data["target"].apply(lambda x:1 if x>0 else 0)


EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in text_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = getVectors(w,1)[0]
        #embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_text_matrix[i][j] = embedding_vector.decode().split(" ")
            #final_text_matrix[i][j] = embedding_vector
        j=j+1
        if j==60: break
    i=i+1
    
final_text_matrix[final_text_matrix==0]=np.nan


MAX_CAT_LENGTH=4

final_cat_matrix=np.zeros((len(text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
i=0
for p in cat_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = getVectors(w,1)[0]
        #embedding_vector = embeddings_index.get(w)
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_text_matrix[i][j] = embedding_vector.decode().split(" ")
            #final_cat_matrix[i][j] = embedding_vector
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


    
final_sentence_matrix=np.zeros((len(text_X),2, EMBEDDING_DIM))        


for p in range(len(text_X)):
    final_sentence_matrix[p][0]=np.nanmean(final_text_matrix[p],axis=0)
    final_sentence_matrix[p][1]=np.nanmean(final_cat_matrix[p],axis=0)
    #final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
    
final_sentence_matrix[np.isnan(final_sentence_matrix)] = 0

final_sentence_matrix_train, final_sentence_matrix_test, trainY, testY = train_test_split(final_sentence_matrix, y, test_size=0.25, random_state=0)

mt=time.time()
text_model = Sequential()
text_model.add(Conv1D(64, 1, activation='relu',input_shape=(2,EMBEDDING_DIM)))
text_model.add(GlobalMaxPooling1D())

text_input=Input(shape=(2,EMBEDDING_DIM))
encoded_text=text_model(text_input)

#senti_input=Input(shape=(1,))

#merged = concatenate([encoded_text, senti_input])


merged = Dense(100, activation='relu')(encoded_text)
merged = Dense(64, activation='relu')(merged)
merged = Dense(32, activation='relu')(merged)

main_output = Dense(1, activation='linear')(merged)

model = Model(inputs=[text_input], outputs=[main_output])
model.compile(
        optimizer=optimizers.Adam(lr=1e-3, decay=1e-3 / 200
                                  #,lr=0.01, decay=0.0
                                  , beta_1=0.9, beta_2=0.999, amsgrad=False), 
        #optimizer="sgd", 
        loss='mse'
        #, metrics=['mape', 'acc']
        )
# summarize the model
print(model.summary())
# fit the model
#model.fit(final_input_matrix, labels, epochs=20, verbose=2,validation_split=0.2)
model.fit([np.array(final_sentence_matrix_train)], np.array(trainY),validation_data=([np.array(final_sentence_matrix_test)], testY),
           epochs=200, verbose=2,batch_size=100)
tmt=time.time()-mt
print("time taken for train:: ",tmt)



test_predY=model.predict([np.array(final_sentence_matrix_test)])


#test_total_data=pd.read_csv("processed_virality_data.csv")

#test_total_data=total_data[total_data["text"].notnull()]

'''

test_total_data=total_data[100000:100100]


test_text_X=test_total_data["text"]
test_cat_X=test_total_data["category"]
test_key_X=test_total_data["keys"]
test_senti_X=test_total_data["sentiment"]
test_type_X=test_total_data["type"]
test_y=test_total_data["target"]



EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

test_final_text_matrix=np.zeros((len(test_text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in test_text_X:
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

test_final_cat_matrix=np.zeros((len(test_text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
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


    
test_final_sentence_matrix=np.zeros((len(test_text_X),2, EMBEDDING_DIM))        


for p in range(len(test_text_X)):
    test_final_sentence_matrix[p][0]=np.nanmean(test_final_text_matrix[p],axis=0)
    test_final_sentence_matrix[p][1]=np.nanmean(test_final_cat_matrix[p],axis=0)
    #final_sentence_matrix[p][2]=np.nanmean(final_key_matrix[p],axis=0)
    
test_final_sentence_matrix[np.isnan(test_final_sentence_matrix)] = 0

trained_model=load_model("virality_prediction_1L")
test_predY=trained_model.predict([np.array(test_final_sentence_matrix)])