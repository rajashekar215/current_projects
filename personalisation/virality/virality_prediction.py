# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import re
from categoryapi import *
from util import *
from sentiment_analyzer import *
from vader import *
from indic_tagger.pipeline import *
from telugu_word_embeddings import *
import time
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential,Model
from keras.layers import Dense,Conv1D,MaxPooling1D,GlobalAveragePooling1D,Dropout,GlobalMaxPooling1D,Input,concatenate
from keras import optimizers
from sklearn.model_selection import train_test_split

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
    return ' '.join(new_doc).replace("\u200c"," ")

total_data=pd.read_csv("virality_dataset_telugu.csv")

total_data=total_data[total_data["post_desc"].notnull()]

total_data=total_data[:20000]

docs=total_data[['post_title', 'post_desc','category_name', 'type']]

y=total_data.apply(lambda x:(x["installs"]/x["shares"] if x["shares"]!=0 else 0),axis=1)


text_X=[]
cat_X=[]
key_X=[]
sia= SentimentIntensityAnalyzer()
senti_X=[]
type_X=[]
for index,doc in docs.iterrows():
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
        s=clean_text(doc["post_desc"])
        catg=catg+category(s)
# =============================================================================
#         sentiment=sia.polarity_scores(s)["compound"]
#         tags=getTaggers(doc["post_desc"],"te")
#         if 'NN' in tags and len(tags['NN'])>0:
#             keys=keys+' '.join(tags['NN'])
#         if 'NNP' in tags and len(tags['NNP'])>0:
#             keys=keys+" "+' '.join(tags['NNP'])
#         if 'VM' in tags and len(tags['VM'])>0:
#             keys=keys+" "+' '.join(tags['VM'])
# =============================================================================
    else:
        if "category" in doc and doc["category"]: catg=catg+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        else:catg="Nothing"
        if "post_title" in doc and doc["post_title"] and doc["post_title"]!='':
                s=clean_text(doc["post_title"])
# =============================================================================
#                 sentiment=sia.polarity_scores(s)["compound"]
#                 tags=getTaggers(doc["post_title"],"te")
#                 if 'NN' in tags and len(tags['NN'])>0:
#                     keys=keys+' '.join(tags['NN'])
#                 if 'NNP' in tags and len(tags['NNP'])>0:
#                     keys=keys+" "+' '.join(tags['NNP'])
#                 if 'VM' in tags and len(tags['VM'])>0:
#                     keys=keys+" "+' '.join(tags['VM'])
# =============================================================================
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
    key_X.append(clean_text(keys))
    senti_X.append(sentiment)
    type_X.append(doc["type"])

processed_data = pd.concat(
    [
        total_data,
        pd.DataFrame(
    {'text': text_X,
     'category': cat_X,
     'keys': key_X,
     'type':type_X,
     'sentiment':senti_X,
     'target':y
    })
    ], axis=1
)
    
# =============================================================================
# processed_data = pd.DataFrame(
#     {'text': text_X,
#      'category': cat_X,
#      'keys': key_X,
#      'type':type_X,
#      'sentiment':senti_X,
#      'target':y
#     })
# =============================================================================

processed_data.to_csv("processed_virality_data.csv")

# =============================================================================
# label_encoder = LabelEncoder()
# label_type = label_encoder.fit_transform(type_X)
# encoded_type=to_categorical(label_type,3)
# 
# =============================================================================
EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in text_X:
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

final_cat_matrix=np.zeros((len(text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
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
                                  , beta_1=0.9, beta_2=0.999, epsilon=None, amsgrad=False), 
        #optimizer="sgd", 
        loss='mean_absolute_error'
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

# =============================================================================
# et=time.time()
# # evaluate the model
# loss, accuracy = model.evaluate([np.array(final_sentence_matrix)], np.array(y), verbose=0)
# print('Accuracy: %f' % (accuracy*100))
# tet=time.time()-et
# print("time taken for evaluation:: ",tet)
# =============================================================================




# =============================================================================
# total_data=pd.read_csv("virality_dataset_telugu.csv")
# 
# total_data=total_data[total_data["post_desc"].notnull()]
# 
# total_data=total_data[:5000]
# =============================================================================

#docs=total_data[['post_title', 'post_desc','category_name', 'type']]

#y=total_data.apply(lambda x:(x["installs"]/x["shares"] if x["shares"]!=0 else 0),axis=1)



text_X=[]
cat_X=[]
key_X=[]
sia= SentimentIntensityAnalyzer()
senti_X=[]
type_X=[]
for index,doc in docs[:1].iterrows():
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
        s=clean_text(doc["post_desc"])
        catg=catg+category(s)
# =============================================================================
#         sentiment=sia.polarity_scores(s)["compound"]
#         tags=getTaggers(doc["post_desc"],"te")
#         if 'NN' in tags and len(tags['NN'])>0:
#             keys=keys+' '.join(tags['NN'])
#         if 'NNP' in tags and len(tags['NNP'])>0:
#             keys=keys+" "+' '.join(tags['NNP'])
#         if 'VM' in tags and len(tags['VM'])>0:
#             keys=keys+" "+' '.join(tags['VM'])
# =============================================================================
    else:
        if "category" in doc and doc["category"]: catg=catg+cat[doc["category"]] if doc["category"] in cat else doc["category"]
        else:catg="Nothing"
        if "post_title" in doc and doc["post_title"] and doc["post_title"]!='':
                s=clean_text(doc["post_title"])
# =============================================================================
#                 sentiment=sia.polarity_scores(s)["compound"]
#                 tags=getTaggers(doc["post_title"],"te")
#                 if 'NN' in tags and len(tags['NN'])>0:
#                     keys=keys+' '.join(tags['NN'])
#                 if 'NNP' in tags and len(tags['NNP'])>0:
#                     keys=keys+" "+' '.join(tags['NNP'])
#                 if 'VM' in tags and len(tags['VM'])>0:
#                     keys=keys+" "+' '.join(tags['VM'])
# =============================================================================
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
# =============================================================================
#     key_X.append(clean_text(keys))
#     senti_X.append(sentiment)
#     type_X.append(doc["type"])
# 
# =============================================================================

# =============================================================================
# processed_data = pd.DataFrame(
#     {'text': text_X,
#      'category': cat_X,
#      'keys': key_X,
#      'type':type_X,
#      'sentiment':senti_X,
#      'target':y
#     })
# processed_data.to_csv("processed_virality_data.csv")
# =============================================================================

# =============================================================================
# label_encoder = LabelEncoder()
# label_type = label_encoder.fit_transform(type_X)
# encoded_type=to_categorical(label_type,3)
# 
# =============================================================================
EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60

final_text_matrix=np.zeros((len(text_X),MAX_TEXT_LENGTH, EMBEDDING_DIM))        
i=0
for p in text_X:
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

final_cat_matrix=np.zeros((len(text_X),MAX_CAT_LENGTH, EMBEDDING_DIM))        
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


predY=model.predict([np.array(final_sentence_matrix_train)])