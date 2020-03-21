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
#from telugu_word_embeddings import *
import keras
import requests
import json
import re
from categoryapi import *
from allennlp.predictors import Predictor
predictor = Predictor.from_path("output26/model.tar.gz")

# =============================================================================
# results = predictor.predict(sentence='LJP सांसद और रामविलास पासवान के बेटे चिराग ने आज कहा कि LJP के लिए सीटों की संख्या मायने नहीं रखती लेकिन जिस तरीके से संख्याओं का ऐलान किया गया उसके बाद हमारी चिंताएं बढ़ीं हम किसी से नाराज नहीं हैं पर असंतोष जरूर है उन्होंने ये भी कहा कि NDA ने हमें जानकारी कुछ और दी थी और ऐलान कुछ और किया गया चिराग ने कहा हमने अपनी चिंताएं बीजेपी के सामने रख दी हैं जो सुलझा ली जाएंगी')
# 
# nerkeys=[]
# for i in range(len(results["tags"])):
#     if results["tags"][i]!='O':
#         nerkeys.append(results["words"][i])
# =============================================================================
        
def clean_text(text):
    line = text.split(' ')
    new_doc=[]
    for w in line:
        w=re.sub('\s*\d*\s', '', w)
        match_string="[☛.,'\":?<>&\r\n#\s\d;*\-!()/\$।‘’]"
        unmatch_string="[^☛.,'\":?<>&\r\n#\s\d;*\-!()/\$।‘’]"
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
    ct=' '.join(new_doc).replace("\u200c"," ")
    cat=category(ct)
    results = predictor.predict(sentence=ct)
    nerkeys=[]
    for i in range(len(results["tags"])):
        if results["tags"][i]!='O':
            nerkeys.append(results["words"][i])
    nerkeys=list(set(nerkeys))
    nerkeys=' '.join(nerkeys)     
    return pd.Series([ct,cat,nerkeys])





data=pd.read_csv('virality_dataset_hindi.csv')
data=data[data["post_status"].isin(['published','published1','published2','published3','published4'])]

#test_data=data[:10]

#test_data[["text","new_cat","ner_keys"]]=test_data["post_desc"].apply(clean_text)

#text=data[:10]["post_desc"].apply(clean_text)

data[["text","new_cat","ner_keys"]]=data["post_desc"].apply(clean_text)

#data=data[data["post_gmt"]>1483209000]
#data=data[data["post_gmt"]>1514745000]
data=data[data["text"].notnull()]
data = data.sort_values(by=['post_gmt'], ascending=True)

def cat_sort(x):
    #print(x)
    return " ".join(sorted(x.lower().strip().split(" ")))

data["new_cat"]=data["new_cat"].apply(cat_sort)

#y=data["target"].apply(lambda x:1 if x>0 else 0)

data=data[[ 'post_id', 'post_id_encrypted','post_url', 'post_date', 'post_gmt', 'post_title'
           , 'post_desc','source_id', 'source_name', 'post_status', 'post_parent','submitted_id'
           , 'writer_name', 'category_id', 'category_name','lang_id','writer_custid', 'district_ids'
           , 'mandal_id','village_id', 'onetime_text', 'writer_level', 'writer_topic','writer_sub_topic'
           , 'is_breaking', 'shares', 'installs','text', 'type'
           , 'new_cat', 'ner_keys']]

data.to_csv("virality_dataset_hindi_processed.csv")

general_data=data[data["new_cat"]=="general"]

general_data_0=general_data[general_data["target"]==0]

general_data_1=general_data[general_data["target"]>0]

general_data_0 = general_data_0.sort_values(by=['post_gmt'], ascending=True)

general_data_rem=general_data_0[:int(len(general_data_0)/2)]

general_data_0=general_data_0[int(len(general_data_0)/2):]



general_state_data=data[data["new_cat"]=="general state"]

general_state_data_0=general_state_data[general_state_data["target"]==0]

general_state_data_1=general_state_data[general_state_data["target"]>0]

general_state_data_0 = general_state_data_0.sort_values(by=['post_gmt'], ascending=True)

general_state_data_rem=general_state_data_0[:int(len(general_state_data_0)/2)]

general_state_data_0=general_state_data_0[int(len(general_state_data_0)/2):]



state_data=data[data["new_cat"]=="state"]

state_data_0=state_data[state_data["target"]==0]

state_data_1=state_data[state_data["target"]>0]

state_data_0 = state_data_0.sort_values(by=['post_gmt'], ascending=True)

state_data_rem=state_data_0[:int(len(state_data_0)/2)]

state_data_0=state_data_0[int(len(state_data_0)/2):]


rem_data=data[~data["new_cat"].isin(["general","general state","state"])]


new_data=pd.concat([general_data_0,general_data_1,general_state_data_0,general_state_data_1
                    ,state_data_0,state_data_1,rem_data])

removed_data=pd.concat([general_data_rem,general_state_data_rem,state_data_rem])

new_y=new_data["target"].apply(lambda x:1 if x>0 else 0)

new_data.to_csv("virality_limited_data.csv")

removed_data.to_csv("removed_data.csv")



#data.to_csv("virality_all_data.csv")

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

train_total_data=data[:1000]

# =============================================================================
# text_X=train_total_data["text"]
# cat_X=train_total_data["new_cat"]
# key_X=train_total_data["keys"]
# senti_X=train_total_data["sentiment"]
# type_X=train_total_data["type"]
# y=train_total_data["target"].apply(lambda x:1 if x>0 else 0)
# =============================================================================


one_data=train_total_data[train_total_data["target"]>0]

zero_data=train_total_data[train_total_data["target"]==0]


def cat_sort(x):
    #print(x)
    return " ".join(sorted(x.lower().strip().split(" ")))

zero_data["new_cat"]=zero_data["new_cat"].apply(cat_sort)
testing=zero_data[zero_data["new_cat"]=="crime security"]
grouped=testing.groupby("new_cat")

main_list=[]
sim_list=[]
url="http://49.156.128.11:5005/simapi"
#out=[]
for name, group in grouped:
    print(name)
    #group.reset_index(drop=True, inplace=True)
    group=list(group)
    for index,row in enumerate(d for d in group):
        print(row)
        main_list.append(row)
        del group[index]
        #group.drop(index, inplace=True)
        #group.reset_index(drop=True, inplace=True)
        #if row["target"]==0:
            #print(row["text"])
            #zero_group=group[group["target"]==0]
        text_list=list(pd.DataFrame(group)["text"])
            #print(test_list)
        if len(text_list)>0:
            body = {"lang": "Telugu", "text1":row["text"], "text2":text_list,"le":len(text_list)}
            x = requests.post(url, json = body,headers={"Content-Type": "application/json"})
            print(json.loads(x.text)["simlist"])                
            simid=json.loads(x.text)["simlist"]
            for s in simid:
                if s:
                    print(row["text"],text_list[s[0]])  
                    sim_list.append(group.iloc[0].to_dict())
                    del group[s[0]]
                    #print(group.index)
                    #group.drop(s[0], inplace=True)
                        
                        
            



            
   
            
        

