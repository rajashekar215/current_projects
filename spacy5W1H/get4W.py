# -*- coding: utf-8 -*-
import spacy
import neuralcoref
import re
from dateutil.parser import parse
import datetime


nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

def your_while_generator(n):
    while True:
        yield n
        if n.pos_=="NOUN":
            break
        try:
            n=n.nbor()
        except:
            break

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
    return {'who':agent_action[0]['main'],'what':agent_action[0]['VN_phrase']}


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    acceptable_dates={'today':0,'yesterday':86400,'tomorrow':86400}
    unacceptable_dates=['^\d+$']
    
    first_step=True
    for und in unacceptable_dates:
        if re.search(rf'{und}',string):
            first_step=False
    
    if not first_step:
        return (False,None)
    else:
        if string.lower() in acceptable_dates.keys():
            return (True,acceptable_dates[string.lower()])
        else:
            try: 
                #parse(string, fuzzy=fuzzy)
                diff=abs((datetime.datetime.now()-parse(string, fuzzy=fuzzy)).total_seconds())
                return (True,diff)
        
            except ValueError:
                return (False,None)
            

def environment_extractor(doc,text_doc,persons):
    loc=[]
    loc_slist=[]
    dates=[]
    max_diff=0
    for ent in doc.ents:
        if ent.label_ in ['GPE','LOC','ORG','FAC'] and ent.text not in ' '.join(persons):
            score=0
            if ent.label_ in ['GPE','LOC']:
                score+=1
            print(ent.text,ent.label_)
            #loc_start=ent.text.split(" ")[0]
            loc_start=' '+ent.text
            if loc_start not in loc_slist:
                loc_slist.append(loc_start)
                loc_pos=text.find(loc_start)
                frequency=len([i for i in range(len(text)) if text.startswith(loc_start, i)] )
                score+=(len(text)-loc_pos)/len(text)
                score+=frequency/len(text_doc)
                score=score/3
                loc_doc={'loc':ent.text}
                loc_doc['loc_pos']=loc_pos
                loc_doc['loc_freq']=frequency
                loc_doc['tag']=ent.label_
                loc_doc['score']=score
                loc.append(loc_doc)
        if ent.label_ in ['DATE']:
            print(ent.text,ent.label_)
            date_test=is_date(ent.text)
            if date_test[0]:
                dates.append({'date':ent.text,'diff':date_test[1],'tag':ent.label_})
                if date_test[1]>max_diff:
                    max_diff=date_test[1]
                    
    date_slist=[]
    for d in dates:
            date_start=d['date']
            if date_start not in date_slist:
                date_slist.append(date_start)
                date_pos=text.find(date_start)
                frequency=len([i for i in range(len(text)) if text.startswith(date_start, i)] )
                score=(len(text)-date_pos)/len(text)
                score+=frequency/len(text_doc)
                score+=(max_diff-d['diff'])/max_diff
                score=score/3
                d['date_pos']=date_pos
                d['date_freq']=frequency
                d['score']=score
    
    ret_doc={}  
    if len(loc)>0:          
        loc=sorted(loc,key=lambda x:x["score"],reverse=True)
        ret_doc['where']=loc[0]['loc']
    else:
        ret_doc['where']=None
    
    if len(dates)>0:          
        dates=sorted(dates,key=lambda x:x["score"],reverse=True)
        ret_doc['when']=dates[0]['date']
    else:
        ret_doc['when']=None
    
    return ret_doc
    
    

def extract_4W(text):
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
    
    final_doc={}
    action_doc=action_extractor(doc,text_doc,ner)    
    final_doc.update(action_doc)
    env_doc=environment_extractor(doc,text_doc,persons)    
    final_doc.update(env_doc)
    return final_doc

#text='''BJP's Kapil Mishra criticised those calling for his arrest following his remarks ahead of the violence in North-East Delhi. "Those who did not consider Burhan Wani and Afzal Guru as terrorists, are calling Kapil Mishra a terrorist," Mishra tweeted. "Those who go to court to get Yakub Memon...released are demanding arrest of Kapil Mishra. Jai Shri Ram," he added.'''
#4W_doc=extract_4W(text)
