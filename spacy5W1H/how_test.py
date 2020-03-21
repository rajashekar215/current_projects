# -*- coding: utf-8 -*-
import spacy
import neuralcoref
import re
from dateutil.parser import parse
import datetime

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

text='''As many as two suspects have been arrested and have been brought to a police station by Delhi Police for spreading rumours of violence and scare. This comes after reports of communal tension in Tilak Nagar and Khyala area were circulated on social media. Delhi Police had denied the reports, saying, "There is no truth behind it."'''

doc=nlp(text)
    
copulative_conjunction = ['and', 'as', 'both', 'because', 'even', 'for', 'if ', 'that', 'then', 'since', 'seeing',
                               'so', 'after']    

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                   'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
                   'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                   'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                   'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
                   'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                   'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                   'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                   'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                   'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
                   'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn',
                   'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won',
                   'wouldn', ':', '.', '"', ';', ',', '\'']

stop_ner = ['TIME', 'DATE', 'ORGANIZATION', 'DURATION', 'ORDINAL']

# end of sentence, quote, PERIOD, COLON, QUOTE
blacklist = ['.']#, '"', '\'', ';']

stop_ner=[]
for ent in doc.ents:
    if ent.text not in stop_ner and ent.label_ in ['TIME', 'DATE', 'ORGANIZATION', 'DURATION', 'ORDINAL']:
        stop_ner.append(ent.text)


methods_list=[]
for token in doc:
    if token.text.lower() in copulative_conjunction:
        n=token
        print(n)
        stree=''
        while n:
            if n.lemma_ not in blacklist and n.text not in stop_ner:
                stree+=n.text_with_ws
                try:
                    n=n.nbor()
                except:
                    break
            else:
                break
        print(stree)
        m_doc={'root':token.text}
        m_doc['extracted_method']=stree
        score=1
        score+=(len(text)-text.index(m_doc['extracted_method']))/len(text)
        m_doc['score']=score/2
        methods_list.append(m_doc)
    elif token.pos_ in ['ADJ','ADV']:
        n=token
        stree=''
        while n:
            if n.lemma_ not in blacklist and n.text not in stop_ner:
                stree+=n.text_with_ws
                try:
                    n=n.nbor()
                except:
                    break
            else:
                break
        #print(stree)
        m_doc={'root':token.text}
        m_doc['extracted_method']=stree
        score=0
        score+=(len(text)-text.index(m_doc['extracted_method']))/len(text)
        m_doc['score']=score/2
        methods_list.append(m_doc)
        
methods_list=sorted(methods_list,key=lambda x:x['score'],reverse=True)        
        
        
for token in doc:
    print (token, token.tag_, token.pos_, spacy.explain(token.tag_))
    
spacy.displacy.serve(doc, style='dep')

spacy.displacy.serve(doc, style='ent')

doc._.coref_clusters


for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char,
          ent.label_, spacy.explain(ent.label_))    

doc=nlp(text)

text_doc=[]
for token in doc:
    text_doc.append(token.text)

ner={}
persons=[]
for ent in doc.ents:
    if ent.text not in ner:
        ner[ent.text]=ent.label_
        if ent.label_=='PERSON':
            persons.append(ent.text)


causal_entities=[]
for ent in doc.ents:
    if ent.label_ not in ["DATE","TIME"]:
        causal_entities.append(ent.text)
        #print(ent.text, ent.start_char, ent.end_char,
              #ent.label_, spacy.explain(ent.label_))  

NPN=[]
for token in doc:
    if token.pos_ in ["NOUN","PROPN"]:
        NPN.append(token.text)
