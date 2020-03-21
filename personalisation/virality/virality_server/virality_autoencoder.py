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
from getVectors import *



data=pd.read_csv('virality_data_updated.csv')

data=data[data["post_gmt"]>1483209000]
data=data[data["text"].notnull()]
data = data.sort_values(by=['post_gmt'], ascending=True)

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

train_total_data=data[:6000]

text_X=train_total_data["text"]
cat_X=train_total_data["new_cat"]
key_X=train_total_data["keys"]
senti_X=train_total_data["sentiment"]
type_X=train_total_data["type"]
y=np.array(train_total_data["target"].apply(lambda x:1 if x>0 else 0))


EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
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

for p in text_X:
    awords=p.split(" ")
    #print(len(awords))
    j=0
    for w in awords:
        embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_text_matrix[i][j] = embedding_vector.decode().split(" ")
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
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_cat_matrix[i][j] = embedding_vector.decode().split(" ")
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

new_input_matrix=np.hstack((np.nanmean(final_text_matrix,axis=1),np.nanmean(final_cat_matrix,axis=1)))
    
new_input_matrix[np.isnan(new_input_matrix)] = 0

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
    print(i,trainY[i])
    if trainY[i]==0:
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
encoder=Dense(encoding_dim,activation="tanh", 
                activity_regularizer=regularizers.l1(10e-5)
                )(input_layer)
encoder=keras.layers.Dropout(0.3)(encoder)
encoder=Dense(int(encoding_dim/2),activation="selu", 
                #activity_regularizer=regularizers.l1(10e-5)
                )(encoder)
encoder=keras.layers.Dropout(0.4)(encoder)
encoder=Dense(int(encoding_dim/4),activation="selu", 
                activity_regularizer=regularizers.l1(10e-5)
                )(encoder)
encoder=keras.layers.Dropout(0.4)(encoder)
decoder = Dense(int(encoding_dim / 4), activation='tanh')(encoder)
decoder = Dense(int(encoding_dim / 2), activation='selu')(decoder)
decoder = Dense(input_dim, activation='selu')(decoder)
autoencoder = Model(inputs=input_layer, outputs=decoder)

nb_epoch = 100
batch_size = 128
adam=keras.optimizers.Adam(lr=0.00001)
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


threshold = 0.00045

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
                             precision_recall_fscore_support)
y_pred = [1 if e > threshold else 0 for e in error_df.reconstruction_error.values]
conf_matrix = confusion_matrix(error_df.true_class, y_pred)
#plt.figure(figsize=(12, 12))
sns.heatmap(conf_matrix, xticklabels="x", yticklabels="y", annot=True, fmt="d");
plt.title("Confusion matrix")
plt.ylabel('True class')
plt.xlabel('Predicted class')
plt.show()      
