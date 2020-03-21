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
from keras.models import Sequential
from keras.layers import Dense,Conv1D,Conv2D,MaxPooling1D,MaxPooling2D,GlobalAveragePooling1D,Dropout,GlobalMaxPooling1D
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
from pos_tagging import *
import multiprocessing as mp
from keras.models import load_model
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 



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
#cat_list=list(mdb["user_keywords_data"].find({"custid" : custid},{"_id":0,"category":1}))[0]["category"]     


documents=mdb.rating_points.find({"custid" : custid},{"category":1,"keywords":1,"post_desc":1,"rating":1})
docs=list(documents)
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


    

def preprocess_pool(doc):
    s=''
    if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
    if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
    if "post_desc" in doc and doc["post_desc"]:
        #print(doc["post_desc"])
        #tag_list=[]
        #tag_list=pool.apply_async(tag,args=[doc["post_desc"]])
        #tags=pool.apply(tag,args=(doc["post_desc"]))
        tag_list=tag(doc["post_desc"])
        #print(tag_list)
        for t in tag_list:
            s=s+" "+t["word"]+"_"+t["tag"]
    return {"x":s,"y":doc["rating"]}
    
#pool = mp.Pool(mp.cpu_count())

#results=[]
#for doc in docs[:20]:
#pool.apply_async(preprocess_pool,args=[doc],callback=results.append)
# =============================================================================
# result=pool.map(preprocess_pool,docs)
# 
# df=pd.DataFrame(result)
# X=df.iloc[:,0]
# y=df.iloc[:,1]
# =============================================================================
#y=pool.map(preprocess_y,docs)

#print(X)
#print(y)
    


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


def count_words(count_dict, text):
    '''Count the number of occurrences of each word in a set of text'''
    for sentence in text:
        for word in sentence.split():
            if word not in count_dict:
                count_dict[word] = 1
            else:
                count_dict[word] += 1

data_X=[]
y=[]

for doc in docs:
    #print(doc)
    s=''
    if "category" in doc and doc["category"]: s=s+cat[doc["category"]] if doc["category"] in cat else doc["category"]
    #if "keywords" in doc and doc["keywords"]: s=s+" "+" ".join(doc["keywords"])
    if "post_desc" in doc and doc["post_desc"]:
        s=s+" "+doc["post_desc"]
# =============================================================================
#         tag_list=tag(doc["post_desc"])
#         #print(tag_list)
#         for t in tag_list:
#             s=s+" "+t["word"]+"_"+t["tag"]
# =============================================================================
    data_X.append(s)
    y.append(doc["rating"])
#pool.close()
#pool.join()
#print(X[:2])
cleaned_X=[]
for d in data_X:    
    cleaned_X.append(clean_text(d))

word_counts = {}

count_words(word_counts, cleaned_X)

print("Size of Vocabulary:", len(word_counts))

embeddings_index = {}
with open('telugu.vec', encoding='utf-8', newline='\n', errors='ignore') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = embedding
        
        

print('Word embeddings:', len(embeddings_index))
            
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
        

final_input_matrix=np.zeros((len(cleaned_X),100, EMBEDDING_DIM))        
i=0
for p in cleaned_X:
    awords=p.split(" ")
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_input_matrix[i][j] = embedding_vector
        j=j+1
    i=i+1
        


# =============================================================================
# vec = HashingVectorizer(decode_error = 'ignore',n_features=2**18)
# sparse_X = vec.transform(data_X)
# 
# from sklearn.decomposition import TruncatedSVD
# svd = TruncatedSVD(100)
# X = svd.fit_transform(sparse_X)
# 
# print(X.shape)
# =============================================================================

labels=y
#labels=keras.utils.to_categorical(y, num_classes=6)
# =============================================================================
# max_length = 50
# vocab_size = 100000
# encoded_docs = [one_hot(d, vocab_size) for d in X]
# #print(encoded_docs)
# # pad documents to a max length of 4 words
# 
# padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
# =============================================================================
t1=time.time()-t0
print("time taken for preprocess",t1)
#print(padded_docs)
# define the model
mt=time.time()

MAX_SEQUENCE_LENGTH=100
# =============================================================================
# model.add(Embedding(len(word_counts) + 1,
#                             EMBEDDING_DIM,
#                             weights=[embedding_matrix],
#                             input_length=MAX_SEQUENCE_LENGTH,
#                             trainable=False))
# =============================================================================

model = Sequential()
#model.add(keras.layers.InputLayer(input_shape=(200,300)))
#model.add(Conv2D(128, (5,5), activation='relu'))
#model.add(MaxPooling2D(5,5))
#model.add(Conv2D(128, (5,5), activation='relu'))
#model.add(MaxPooling2D(5,5))
model.add(Conv1D(10, 5, activation='relu',input_shape=(100,300)))
model.add(MaxPooling1D(2))
model.add(Conv1D(20, 5, activation='relu'))
model.add(MaxPooling1D(2))
model.add(Conv1D(10, 5, activation='relu'))
model.add(MaxPooling1D(2))
#model.add(GlobalMaxPooling1D())
model.add(Flatten())
model.add(Dense(50, activation='relu'))
#model.add(Dense(50, activation='relu'))
#model.add(MaxPooling1D(3))
#model.add(Flatten())
#model.add(Conv1D(160, 10, activation='relu'))
#model.add(GlobalAveragePooling1D())
#model.add(Dropout(0.5))
model.add(Dense(6, activation='softmax'))
#print(model.summary())
#model.add(Dense(100, input_shape = (embedding_matrix.shape[1],), activation = 'relu'))
#model.add(Embedding(vocab_size, 50, input_length=max_length))
#model.add(Flatten())
#model.add(Dense(30, activation='relu'))
#model.add(Dense(10, activation='relu'))
#model.add(Dense(6, activation='softmax'))
# compile the model
model.compile(
        optimizer=keras.optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False), 
        #optimizer="rmsprop", 
        loss='sparse_categorical_crossentropy', 
        metrics=['acc'])
# summarize the model
print(model.summary())
# fit the model
model.fit(final_input_matrix, labels, epochs=50, verbose=2)
tmt=time.time()-mt
print("time taken for train:: ",tmt)

et=time.time()
# evaluate the model
loss, accuracy = model.evaluate(final_input_matrix, labels, verbose=0)
print('Accuracy: %f' % (accuracy*100))
tet=time.time()-et
print("time taken for evaluation:: ",tet)
model.save(str(custid))





#del model
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
    if "post_desc" in doc and doc["post_desc"]:
        s=s+" "+doc["post_desc"]
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

#test_x=["రాజకీయాలు  telangana kaleshwaram godhavari ellampalli","వినోదం movies manmadhudu-2"]
#test_x=X
# =============================================================================
# max_length = 50
# vocab_size=100000
# test_encoded_docs = [one_hot(d, vocab_size) for d in test_x]
# #print(test_encoded_docs)
# # pad documents to a max length of 4 words
# 
# test_padded_docs = pad_sequences(test_encoded_docs, maxlen=max_length, padding='post')
# =============================================================================
#print(test_padded_docs)
#model1=load_model(str(custid))


cleaned_test_X=[]
for d in test_x:    
    cleaned_test_X.append(clean_text(d))

test_word_counts = {}

count_words(test_word_counts, cleaned_test_X)

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

final_input_matrix_test=np.zeros((len(cleaned_test_X),100, EMBEDDING_DIM))        
i=0
for p in cleaned_test_X:
    awords=p.split(" ")
    j=0
    for w in awords:
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            final_input_matrix_test[i][j] = embedding_vector
        j=j+1
    i=i+1

# =============================================================================
# vec2 = HashingVectorizer(decode_error = 'ignore',n_features=2**18)
# test_sparse_X = vec2.transform(test_x)
# #svd2 = TruncatedSVD(100)
# test_padded_docs = svd.transform(test_sparse_X)
# =============================================================================
#test_padded_docs=vec.transform(test_x)
pred_y=model.predict_classes(final_input_matrix_test)
#print(pred_y)
t5=time.time()-t4
print("time taken for test:: ",t5)



results = confusion_matrix(test_y, pred_y) 
print('Confusion Matrix :')
print(results) 
print('Accuracy Score :',accuracy_score(test_y, pred_y) )
print('Report : ')
print(classification_report(test_y, pred_y) )








