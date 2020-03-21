# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import re
from getVectors import *

#data=pd.read_csv("teluguposts1l.csv")
#data3=pd.read_csv("teluguposts3m.csv")
#data1=pd.read_csv("teluguposts50k.csv")
data=pd.read_csv("teluguposts4m.csv")

stopwords =["వారు","ఈ","అనే","ద్వారా","తేదీ","జిల్లాలోని","ఆ","మధ్య","ముందు","గ్రామంలో","శ్రీ","తమ","గ్రామ","భారీ","ఉన్న","వారికి","నుంచి","వరకు","జిల్లా","ప్రతి","చేశారు","ఉందని","గత","చెందిన","ఉంది","అని","జరిగిన","అటు","కాగా","వారి","కోసం","మరియు","అన్ని","పార్టీ","పాటు","చేసిన","వద్ద","కూడా","మరో","కలిసి","ఓ","సంఘం","పలు","వచ్చే","ఒక","ప్రత్యేక","జరిగే","జిల్లాలో","అయితే","నుండి","తన","మేరకు","పోటీ","వచ్చిన","గల","తరగతి","సంఖ్యలో","వల్ల","ఉన్నారు","పలువురు","గురించి", "తెలిపారు","ఆయన","రూ","సందర్భంగా","పాల్గొన్నారు","అన్నారు","న","దీంతో","నిర్వహించారు","ఏర్పాటు","వ","లో","చేయాలని","పేర్కొన్నారు","చేసింది","కోరారు","చేసి","తెలిపింది","ఆమె","చెప్పారు","చేస్తున్నారు","జరిగింది","తర్వాత","వెంటనే","వెల్లడించారు","ఏ","మాత్రమే","కోరుతున్నారు","తెలుస్తోంది","తెలిసిందే","తాను","కు","ఇప్పటికే","ఎలాంటి","నిర్వహించిన","దీనిపై","ఇటీవల","ఇది","చేసే","తీసుకోవాలని","పేర్కొంది","చేపట్టారు","చేస్తున్న","గో","చేసినట్లు","చేయడం","మాత్రం","ఉండగా","ఇక","చేసేందుకు","ఇందులో","చేశాడు","తనకు","ఇచ్చారు","చేస్తామని","ను","ఇచ్చిన","చేస్తూ","జరుగుతున్న","గా","మీ","అలాగే","చేసుకోవాలని","ఇవ్వాలని","చేయగా","తో","తమకు","ఉండాలని","ఉండే","ఇదే","తూ","చేస్తున్నట్లు","వచ్చి","వాటిని","ఇప్పుడు","చేసుకున్నారు","ఉంటే","ఉన్నాయి","చేస్తే","ఉంటుంది","వేసి","అంటూ","చేసుకుంది","ఇలా","తనను","వెళ్లి","అయిన","మాట్లాడుతూ","చేపట్టిన","తెలిపాడు","వస్తున్న","కానుంది","ఉండటంతో","చేసుకున్న","అందించారు","ఇలాంటి","వచ్చింది","అదే","మన","వే","దీన్ని","తీసుకున్నారు","అందులో","కావాలని","అందరూ","ఉన్నాయని","చేయనున్నారు","చేయనున్నట్లు","చేసారు","మాట్లాడారు","అక్కడ","అండ్","ఉ","చేసుకుని","నా","ఉందన్నారు","అందరికీ","చేస్తానని","ఆయనకు","చేస్తోంది","నేను","చేశామని","ఇందుకు","ఇక్కడ","చేస్తామన్నారు","చెబుతున్నారు","దీనిని","ని","అందుకే","ఇప్పటి","చెప్పాడు","మా","వాటి","ఉంటాయని","అంటున్నారు","చేయనుంది","అయింది","అన్న","తేది","ఎన్ని","తమను","అన్నాడు","ఎప్పుడు","చేస్తుండగా","చేసుకున్నాడు","ఎప్పుడూ","చేస్తుందని","చేస్తుంది","చేస్తున్నామని","దాన్ని","చేశామన్నారు","చేస్తున్నాయి","చెప్తున్నారు","ల","ఢీ","అందిస్తామని","చేస్తారని","చేసిందని","అవుతుంది","అందుకు","చేస్తారు","అతను","చేపట్టింది","చేస్తోందని","చేసుకోవచ్చని","చేసుకోవచ్చు","చేయనున్న","మీకు","చేస్తున్నాం","గారు","మండలం","లోని","గారి","లు","గారిని","గారికి","లకు","లోకి","జి","వారిని","చేయుచున్నారు"]

pun=[',','*','@','!','.',"'",'%','#',":","?",'>','--','↓',"(",")","<"]
     
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
                    new_doc.extend([ww for ww in w if ww!=""])
            except:
                if w!="":
                    new_doc.append(w)
    return ' '.join(new_doc).replace("\u200c"," ")


data['post_desc']=data['post_desc'].apply(clean_text)

processed_data=[]
for doc in data['post_desc']:
    owords=doc.split(" ")
    words=[ w  for w in owords if w not in stopwords and w!='']
    processed_data.append(words)

EMBEDDING_DIM=300
MAX_TEXT_LENGTH=60
new_input_matrix=np.zeros((processed_data, EMBEDDING_DIM))        

i=0
for doc in processed_data:
    text_array=np.zeros((MAX_TEXT_LENGTH, EMBEDDING_DIM))
    j=0
    for w in doc:
        embedding_vector = embeddings_index.get(w)
        #embedding_vector = getVectors(w,1)[0]
        #print(embedding_vector[:3])
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            text_array[j] = embedding_vector
            #text_array[j] = embedding_vector.decode().split(" ")
        j=j+1
        if j==60: break 
    
    text_array[text_array==0]=np.nan
    new_input_matrix[i]=np.nanmean(text_array,axis=0)
    i=i+1
    
new_input_matrix[np.isnan(new_input_matrix)] = 0
np.savetxt('cat_input_data_telugu.txt', new_input_matrix)
