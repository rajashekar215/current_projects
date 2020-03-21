# -*- coding: utf-8 -*-
import spacy
import neuralcoref
import textacy
import re
from dateutil.parser import parse
import datetime

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

text='''BJP's Kapil Mishra criticised those calling for his arrest following his remarks ahead of the violence in North-East Delhi. "Those who did not consider Burhan Wani and Afzal Guru as terrorists, are calling Kapil Mishra a terrorist," Mishra tweeted. "Those who go to court to get Yakub Memon...released are demanding arrest of Kapil Mishra. Jai Shri Ram," he added.'''

doc=nlp(text)

text_doc=[]
for token in doc:
    text_doc.append(token.text)

for token in doc:
    print (token, token.tag_, token.pos_, spacy.explain(token.tag_))
    
spacy.displacy.serve(doc, style='dep')

spacy.displacy.serve(doc, style='ent')

matcher = spacy.matcher.Matcher(doc.vocab)
def extract_full_name(nlp_doc):
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('FULL_NAME', None, pattern)
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text

extract_full_name(doc)

for token in doc:
    print (token.text, token.tag_, token.head.text, token.dep_)
    
for chunk in doc.noun_chunks:
    print (chunk)    

doc._.coref_clusters

ent_doc={}
max_chain=0
for entity in doc._.coref_clusters:
    ent=str(entity).split(":")[0]
    m_list=[i.strip() for i in re.sub(r'[\[|\]]','',str(entity).split(":")[1]).split(",")]
    ent_doc[ent]=len(m_list)
    if len(m_list)>max_chain:
        max_chain=len(m_list)

who_doc={}        
for ent,chain in ent_doc.items():
    score=chain/max_chain
    score+=(len(text)-text.index(ent))/len(text)
    who_doc[ent]=score/2
    

#pattern = r'(<DET>?<ADP>?<ADJ>?<PROPN|PART|NOUN>+<VERB>?<ADV>*<VERB>+<DET>?<VERB>?<ADP>?<ADJ>?<PROPN|PART|NOUN>+)'
about_talk_doc = textacy.make_spacy_doc(text,lang='en_core_web_sm')
pattern = r'(<DET>?  <NOUN|PROPN>+<VERB>?<ADV>*<VERB>+<DET>?<NOUN|PROPN>+)'
NVN_res = textacy.extract.pos_regex_matches(about_talk_doc, pattern)
# Print all Verb Phrase
NVN_phrases=[]
for chunk in NVN_res:
    print(chunk.text)
    NVN_phrases.append(chunk.text)    

#for token in doc:
    #print(" ".join([t.text for t in token.rights]))
    #if token.dep_=="ROOT" and token.text!='"':
        #print(" ".join([t.text for t in token.children]))


filtered_who_doc={}
what_doc={}
for key in who_doc:
    for phrase in  NVN_phrases:
        if re.search(rf'^{key}',phrase):
            what_doc[re.sub(rf'^{key}','',phrase)]=who_doc[key]
            filtered_who_doc[key]=who_doc[key]

def your_while_generator(n):
    while True:
        yield n
        if n.pos_=="NOUN":
            break
        try:
            n=n.nbor()
        except:
            break

ner=[]
for ent in doc.ents:
    if ent.text not in ner:
        ner.append(ent.text)

agent_action=[]

if len(doc._.coref_clusters)>0:
    agent_action_coref=[]
    max_chain=0
    for entity in doc._.coref_clusters:
        ent=str(entity).split(":")[0]
        m_list=[i.strip() for i in re.sub(r'[\[|\]]','',str(entity).split(":")[1]).split(",")]
        m_list=list(set(m_list))
        print(m_list)
        if len(m_list)>max_chain:
            max_chain=len(m_list)
        m_last_list=[]
        for mention in m_list:
            print(mention)
            m_last=mention.split(" ")[-1]
            if m_last not in m_last_list:
                m_last_list.append(m_last)
                indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
                print(m_last,indexPosList)
                for i in indexPosList:
                    item_doc={}
                    n=doc[i].head
                    if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                        print(n)
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
        if value['main'] in ner:
            score+=1
        value['score']=score/4
if len(list(doc.noun_chunks))>0:
     agent_action_nc=[]
     max_chain=1
     m_last_list=[]
     for chunk in doc.noun_chunks:
         print (chunk)
         m_last=chunk.text.split(" ")[-1]
         if m_last not in m_last_list:
            m_last_list.append(m_last)
            indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
            print(m_last,indexPosList)
            for i in indexPosList:
                item_doc={}
                n=doc[i].head
                if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                    print(n)
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
         if value['main'] in ner:
            score+=1
         value['score']=score/4
            
agent_action=agent_action_coref+agent_action_nc
agent_action=sorted(agent_action,key=lambda x:x['score'],reverse=True)
           
# =============================================================================
# agent_action=[]    
# for entity in doc._.coref_clusters:
#     ent=str(entity).split(":")[0]
#     m_list=[i.strip() for i in re.sub(r'[\[|\]]','',str(entity).split(":")[1]).split(",")]
#     m_list=list(set(m_list))
#     print(m_list)
#     for mention in m_list:
#         #print(mention)
#         m=str(mention)
#         for phrase in  NVN_phrases:
#             #print(phrase)
#             if re.search(rf'^{m}',phrase):
#                 agent_action.append(re.sub(rf'^{m}',ent,phrase))    
# =============================================================================

doc=nlp(text)

text_doc=[]
for token in doc:
    text_doc.append(token.text)
    
doc._.coref_clusters

for token in doc:
    print (token, token.tag_, token.pos_, spacy.explain(token.tag_))



loc=[]
date=[]
loc_slist=[]
for ent in doc.ents:
    if ent.label_ in ['GPE','LOC','ORG','FAC']:
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
                 
loc=sorted(loc,key=lambda x:x["score"],reverse=True)
where=loc[0]['loc']



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
                        
    



for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char,
          ent.label_, spacy.explain(ent.label_))    

dates=[]
max_diff=0
for ent in doc.ents:
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
if len(dates)>0:                 
    dates=sorted(dates,key=lambda x:x["score"],reverse=True)
    when=dates[0]['date'] 
else:
    when=None
    
    
    


