# -*- coding: utf-8 -*-
import spacy
import neuralcoref
import re
from dateutil.parser import parse
import datetime

import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

text='''As many as two suspects have been arrested and have been brought to a police station by Delhi Police for spreading rumours of violence and scare. This comes after reports of communal tension in Tilak Nagar and Khyala area were circulated on social media. Delhi Police had denied the reports, saying, "There is no truth behind it."'''

doc=nlp(text)

for token in doc:
    print (token, token.tag_, token.pos_, spacy.explain(token.tag_))
    
spacy.displacy.serve(doc, style='dep')

spacy.displacy.serve(doc, style='ent')

doc._.coref_clusters


for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char,
          ent.label_, spacy.explain(ent.label_))    

def action_extractor(doc,text_doc,ner):
    agent_action=[]
    agent_action_coref=[]
    agent_action_nc=[]
    if len(doc._.coref_clusters)>0:
        max_chain=0
        for entity in doc._.coref_clusters:
            ent=str(entity).split(":")[0]
            m_list=[i.strip() for i in re.sub(r'[\[|\]]','',str(entity).split(":")[1]).split(",")]
            m_list=list(set(m_list))
            #print(m_list)
            if len(m_list)>max_chain:
                max_chain=len(m_list)
            m_last_list=[]
            for mention in m_list:
                #print(mention)
                m_last=mention.split(" ")[-1]
                if m_last not in m_last_list:
                    m_last_list.append(m_last)
                    indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
                    #print(m_last,indexPosList)
                    for i in indexPosList:
                        item_doc={}
                        n=doc[i].head
                        if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                            #print(n)
                            #verb_string=[ nb.text for nb in your_while_generator(n)]
                            #verb_string=" ".join(verb_string)
                            stree=[t.text for t in n.subtree]
                            verb_string=' '.join(stree[stree.index(m_last)+1:])
                            #print(verb_string)
                            item_doc['main']=ent
                            item_doc['mention']=mention
                            item_doc['mention_pos']=i
                            item_doc['mention_freq']=len(indexPosList)
                            item_doc['VN_phrase']=verb_string
                            item_doc['main_chain']=len(m_list)
                            agent_action_coref.append(item_doc)
        for value in agent_action_coref:
            score=value['main_chain']/max_chain
            score+=(len(text_doc)-value['mention_pos'])/len(text_doc)
            score+=value['mention_freq']/len(text_doc)
            for key in ner.keys():
                if value['main'].lower() in key.lower() or key.lower() in value['main'].lower():
                    score+=1
                    if ner[key]=='Person':
                        score+=1
                    break
            value['score']=score/5
    
    if len(list(doc.noun_chunks))>0:
         max_chain=1
         m_last_list=[]
         for chunk in doc.noun_chunks:
             #print (chunk)
             m_last=chunk.text.split(" ")[-1]
             if m_last not in m_last_list:
                m_last_list.append(m_last)
                indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
                #print(m_last,indexPosList)
                for i in indexPosList:
                    item_doc={}
                    n=doc[i].head
                    if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                        #print(n)
                        #verb_string=[ nb.text for nb in your_while_generator(n)]
                        #verb_string=" ".join(verb_string)
                        stree=[t.text for t in n.subtree]
                        verb_string=' '.join(stree[stree.index(m_last)+1:])
                        #print(verb_string)
                        item_doc['main']=chunk.text
                        item_doc['mention']=chunk.text
                        item_doc['mention_pos']=i
                        item_doc['mention_freq']=len(indexPosList)
                        item_doc['VN_phrase']=verb_string
                        item_doc['main_chain']=1
                        agent_action_nc.append(item_doc)
         for value in agent_action_nc:
             score=value['main_chain']/max_chain
             score+=(len(text_doc)-value['mention_pos'])/len(text_doc)
             score+=value['mention_freq']/len(text_doc)
             for key in ner.keys():
                if value['main'].lower() in key.lower() or key.lower() in value['main'].lower():
                    #print(value['main'],key)
                    score+=1
                    if ner[key]=='PERSON':
                        #print(value['main'],key,'PERSON')
                        score+=1
                    break
             value['score']=score/5
                
    agent_action=agent_action_coref+agent_action_nc
    agent_action=sorted(agent_action,key=lambda x:x['score'],reverse=True)
    return {'who':agent_action[0]['main'],'what':agent_action[0]['VN_phrase'],'act_doc':agent_action}

causal_adpositions={'for':1,'after':1,'because':2, 'hence':2, 'thus':2, 'stemmed':2, 'due':2,
                    'therefore':2, 'consequently':2, 'accordingly':2}

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


patterns_old=['\.([^\.]*) and because of this .*\.','\..* because ([^\.]*)\.','\.([^\.]*) therefore .*\.',
          '\.([^\.]*) hence .*\.','\.([^\.]*) thus .*\.','\.([^\.]*) consequently .*\.','\.([^\.]*) accordingly .*\.',
          '\..* consequence of ([^\.]*)\.','\..* consequences of ([^\.]*)\.','\..* consequence ([^\.]*)\.',
          '\..* effect of ([^\.]*)\.','\.([^\.]*) effect .*\.','\..* result of ([^\.]*)\.','\.([^\.]*) result .*\.',
          '\..* upshot of ([^\.]*)\.','\.([^\.]*) upshot .*\.','\..* outcome of ([^\.]*)\.','\.([^\.]*) outcome .*\.'
          '\..* due to ([^\.]*)\.','\.([^\.]*) due .*\.','\.([^\.]*) stemmed from .*\.','\.([^\.]*) stemmed .*\.',
          '\.([^\.]*) call down .*\.','\.([^\.]*) call forth .*\.','\.([^\.]*) fire up .*\.',
          '\.([^\.]*) give birth .*\.','\.([^\.]*) kick up .*\.','\.([^\.]*) put forward .*\.',
          '\.([^\.]*) set in motion .*\.','\.([^\.]*) set off .*\.','\.([^\.]*) set up .*\.',
          '\.([^\.]*) stir up .*\.']    





post_match_rx=['(?:(?:[\.][^\.]* )+|(?:^[^\.]* )+|^)',' ([^\.]*)']
pre_match_rx=['(([\.][^\.]* )+|(^[^\.]* )+|^)',' (?:[^\.]*)']

post_match_words=['because','consequence of','consequences of','consequence',
                  'effect of','result of','upshot of','outcome of','due to','as',
                  'prevent','ensure']

pre_match_words=['and because of this','therefore','hence','thus','consequently',
                 'accordingly','effect','result','upshot','outcome','due ',
                 'stemmed from','stemmed','call down','call forth','fire up',
                 'give birth','kick up','put forward','set in motion','set off',
                 'set up','stir up','lead to','precipitate','result in','trigger',
                 'commence', 'ignite', 'initiate','set' , 'start'] 

causal_verbs = ['activate', 'actuate', 'arouse', 'associate', 'begin', 'bring', 'call', 'cause', 'commence',
                'conduce', 'contribute', 'create', 'derive', 'develop', 'educe', 'effect', 'effectuate', 'elicit',
                'entail', 'evoke', 'fire', 'generate', 'give', 'implicate', 'induce', 'kick', 'kindle', 'launch',
                'lead', 'link', 'make', 'originate', 'produce', 'provoke', 'put', 'relate', 'result', 'rise', 'set',
                'spark', 'start', 'stem', 'stimulate', 'stir', 'trigger', 'unleash',
                
                'coerce','compel', 'force','evict', 'muzzle','entice','goad', 'inspire',
                'persuade','admit', 'allow' ,'enable', 'let', 'permit','allow', 
                'enable', 'permit', 'tolerate','build', 'create','establish', 'form',
                'produce','continue','keep' , 'maintain', 'perpetuate', 'preserve',
                'activate', 'arouse', 'reactivate', 'revive', 'wake','annihilate',
                'assassinate', 'dismantle', 'extinguish', 'kill','cancel', 'disable',
                'discontinue', 'eliminate','end', 'eradicate','deactivate','decommission',
                'invalidate','neutralize', 'nullify','bring', 'complete','effectuate',
                'implement', 'push','comb', 'debone', 'dehumidify', 'delete', 'detoxify',
                'remove','chime', 'clatter', 'hoot', 'ring', 'rustle','blister', 
                'breach', 'dent', 'equip', 'glaze','retread', 'upholster','include', 
                'inject' , 'poison','salt', 'sweeten','bandage', 'cover', 'plaster',
                'shower' , 'shower','sprinkle', 'sprinkle','brick', 'pack',
                'refill', 'replenish', 'saturate'] 

patterns=[]
for postw in post_match_words:
    patterns.append(post_match_rx[0]+postw+post_match_rx[1])
for prew in pre_match_words:
    patterns.append(pre_match_rx[0]+prew+pre_match_rx[1])

main_text='''As many as two suspects have been arrested and have been brought to a police station by Delhi Police for spreading rumours of violence and scare. This comes after reports of communal tension in Tilak Nagar and Khyala area were circulated on social media. Delhi Police had denied the reports, saying, "There is no truth behind it."'''

doc=nlp(main_text)
text=main_text.lower()

lemma_doc=[]    
for token in doc:
    #print(token.text,token.lemma_)
    if token.lemma_=='-PRON-':
        lemma_doc.append(token.text)
    else:
        lemma_doc.append(token.lemma_)
        
lemmatized_text=' '.join(lemma_doc)

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
 
adp=[]
for p in patterns:
    t=re.findall(r'[a-zA_Z]+',p)
    pt=re.search(r'[a-zA_Z]+(.*)',p)
    why_string=''
    pat=0
    rs=re.search(rf'{p}',text)
    if rs:
        why_string=rs.groups()[0].strip()
        if pt.groups()[0]==post_match_rx[1]:
            pat=1
        else:
            pat=2
    else:
        rs=re.search(rf'{p}',lemmatized_text)
        if rs:
             why_string=rs.groups()[0].strip()
             if pt.groups()[0]==post_match_rx[1]:
                pat=1
             else:
                pat=2
    #print(p)                
    if why_string!='' and t[0]=='as' and text[:text.index(why_string)].index(' as ')>-1:
        continue
    #print(why_string)
    N_exists=False
    for ce in causal_entities:
        if ce in why_string:
            N_exists=True
            break
    if not N_exists:
        for NPNe in NPN:
            if NPNe in why_string:
                N_exists=True
                break
    if N_exists:
        adp_doc={'pattern':p}
        if pat==1:
            adp_doc['cause_phrase']=t[0]+' '+why_string
        elif pat==2:
            adp_doc['cause_phrase']=why_string+' '+t[0]
        score=1
        try:
            score+=(len(text)-text.index(why_string))/len(text)
        except:
            score+=(len(lemmatized_text)-lemmatized_text.index(why_string))/len(lemmatized_text)
        adp_doc['score']=score/2
        adp.append(adp_doc)

verbs=[]
for token in doc:
    if token.pos_=='VERB':
        verbs.append(token)


synsets = []
for verb in causal_verbs:
    synsets += wordnet.synsets(verb, 'v')
final_causal_verbs = set(synsets)


tree_phrases=[]
for v in verbs:
    vsynsets= set(wordnet.synsets(v.text.lower(), 'v'))
    if not vsynsets.isdisjoint(final_causal_verbs):
        print("v:: ",v)
        stree=[i.text_with_ws for i in v.subtree]
        if len(stree)>1:
            #cstr=re.sub(rf'.*{v}',rf'{v}',''.join(stree)).strip(" .").lower()
            cstr=''.join(stree).strip(" .").lower()
            #print("cstr:: ",cstr)
            N_exists=False
            for ce in causal_entities:
                if ce in cstr:
                    N_exists=True
                    break
            if not N_exists:
                for NPNe in NPN:
                    if NPNe in cstr:
                        N_exists=True
                        break
            if N_exists:
                adp_doc={'pattern':v.text}
                adp_doc['cause_phrase']=cstr
                score=(len(text)-text.index(cstr))/len(text)
                adp_doc['score']=score/2
                tree_phrases.append(adp_doc)
                print("t:: ",' '.join(stree))
            
final_why=adp+tree_phrases
final_why=sorted(final_why,key=lambda a:a["score"],reverse=True)            
