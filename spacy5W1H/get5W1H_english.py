# -*- coding: utf-8 -*-
import spacy
import neuralcoref
import re
from dateutil.parser import parse
import datetime
from fake_useragent import UserAgent
from googletrans import Translator
import requests
import itertools
from nltk.corpus import wordnet

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

ua = str(UserAgent().random)

#cause variables
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
    
#method variables
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
                #m_start=re.sub('\'.*','',mention.split(" ")[0])
                if m_last not in m_last_list:
                    m_last_list.append(m_last)
                    indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
                    #print(m_last,indexPosList)
                    for i in indexPosList:
                        item_doc={}
                        n=doc[i].head
                        if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                            print(n)
                            #verb_string=[ nb.text for nb in your_while_generator(n)]
                            #verb_string=" ".join(verb_string)
                            stree=[t.text for t in n.subtree]
                            print(stree)
                            if stree.index(n.text)>(len(stree)-3):
                                verb_string=' '.join(stree)
                            else:
                                verb_string=' '.join(stree[stree.index(m_last)+1:])
                            print(verb_string)
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
                    if ner[key]=='PERSON':
                        score+=1
                    break
            value['score']=score/5
    
    if len(list(doc.noun_chunks))>0:
         max_chain=1
         m_last_list=[]
         for chunk in doc.noun_chunks:
             #print (chunk)
             m_last=chunk.text.split(" ")[-1]
             #m_start=re.sub('\'.*','',chunk.text.split(" ")[0])
             if m_last not in m_last_list:
                m_last_list.append(m_last)
                indexPosList = [ i for i in range(len(text_doc)) if text_doc[i] == m_last ]
                #print(m_last,indexPosList)
                for i in indexPosList:
                    item_doc={}
                    n=doc[i].head
                    if n.pos_=='VERB' and doc[i].text in [t.text for t in n.lefts]:
                        print(n)
                        #verb_string=[ nb.text for nb in your_while_generator(n)]
                        #verb_string=" ".join(verb_string)
                        stree=[t.text for t in n.subtree]
                        print(stree)
                        if stree.index(n.text)>(len(stree)-3):
                            verb_string=' '.join(stree)     
                        else:
                            verb_string=' '.join(stree[stree.index(m_last)+1:])
                        print(verb_string)
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
    acceptable_formats={'today':0,'yesterday':86400,'tomorrow':86400}
    acceptable_dates=['[^\d]*end[^\d]*(\d+)|(\d+)[^\d]*end[^\d]*','[^\d]*start[^\d]*(\d+)|(\d+)[^\d]*start[^\d]*']
    unacceptable_dates=['^\d+$']
    
    first_step=True
    for und in unacceptable_dates:
        if re.search(rf'{und}',string):
            first_step=False
        
    
    if not first_step:
        return (False,None)
    else:
        if string.lower() in acceptable_formats.keys():
            return (True,acceptable_formats[string.lower()])
        else:
            try: 
                #parse(string, fuzzy=fuzzy)
                diff=abs((datetime.datetime.now()-parse(string, fuzzy=fuzzy)).total_seconds())
                return (True,diff)
        
            except ValueError:
                for ad in acceptable_dates:
                    rs=re.search(rf'{ad}',string)
                    if rs:
                        string=rs.groups()[0]
                        first_step=True
                        break
                try: 
                    #parse(string, fuzzy=fuzzy)
                    diff=abs((datetime.datetime.now()-parse(string, fuzzy=fuzzy)).total_seconds())
                    return (True,diff)
        
                except ValueError:
                    return (False,None)
            
def environment_extractor(doc,text_doc,persons,text):
    loc=[]
    loc_slist=[]
    dates=[]
    max_diff=0
    for ent in doc.ents:
        if ent.label_ in ['GPE','LOC','ORG','FAC'] and ent.text not in ' '.join(persons):
            score=0
            if ent.label_ in ['GPE','LOC']:
                score+=1
            #print(ent.text,ent.label_)
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
            #print(ent.text,ent.label_)
            date_test=is_date(ent.text)
            if date_test[0]:
                dates.append({'date':ent.text,'diff':date_test[1],'tag':ent.label_})
                if date_test[1]>max_diff:
                    max_diff=date_test[1]
                    
    #date_slist=[]
    for d in dates:
            date_start=d['date']
            #date_slist.append(date_start)
            date_pos=text.find(date_start)
            frequency=len([i for i in range(len(text)) if text.startswith(date_start, i)] )
            score=(len(text)-date_pos)/len(text)
            score+=frequency/len(text_doc)
            score+=(max_diff-d['diff'])/max_diff if max_diff!=0 else 1
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

def cause_extractor(doc,main_text):
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
                adp_doc['cause_phrase']=why_string
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
                print("cstr:: ",cstr)
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
                    #print("t:: ",' '.join(stree))
                
    final_why=adp+tree_phrases
    final_why=sorted(final_why,key=lambda a:a["score"],reverse=True)
    return {'why':final_why[0]['cause_phrase']}

def method_extractor(doc,text): 
    stop_ner=[]
    for ent in doc.ents:
        if ent.text not in stop_ner and ent.label_ in ['TIME', 'DATE', 'ORGANIZATION', 'DURATION', 'ORDINAL']:
            stop_ner.append(ent.text)
    
    
    methods_list=[]
    for token in doc:
        if token.text.lower() in copulative_conjunction:
            n=token.head.head
            stree=''
            while n:
                if n.lemma_ not in blacklist:# and n.text not in stop_ner:
                    stree+=n.text_with_ws
                    try:
                        n=n.nbor()
                    except:
                        break
                else:
                    break
            #stree=''.join([t.text_with_ws for t in token.head.subtree])
            #print(stree)
            m_doc={'root':token.text}
            m_doc['extracted_method']=stree
            score=1
            score+=(len(text)-text.index(m_doc['extracted_method']))/len(text)
            m_doc['score']=score/2
            methods_list.append(m_doc)
        elif token.pos_ in ['ADJ','ADV'] and token.text.lower() not in stop_words:# and token.text.lower() not in stop_ner:
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
    return {'how':methods_list[0]['extracted_method']}
    
def proxy():
    response = requests.get("https://www.proxy-list.download/api/v1/get?type=http&a}non=elite&country=in")
    proxy = (response.text)
    proxt_list = proxy.split('\r\n')
    proxy_dict = dict(itertools.zip_longest(
        *[iter(proxt_list)] * 2, fillvalue=""))
    return proxy_dict
proxy_dict = proxy()

def get_transalation(text1):
    final_text=[]
    try:
        text1= text1.replace('।','.')
        text1=text1.split('.')
        translator = Translator(service_urls=['translate.google.co.in', 'translate.google.com'], user_agent=ua, proxies=proxy_dict)
        for txt in text1:
            transalation1= translator.translate(txt, dest="en" )
            eng_text= transalation1.text
            final_text.append(eng_text)

        final_text=('. '.join(final_text))
        
        return final_text

    except Exception as e:
        print(e)
        pass    

def extract_5W1H(text):
    #eng_text=get_transalation(text)
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
    env_doc=environment_extractor(doc,text_doc,persons,text)    
    final_doc.update(env_doc)
    cause_doc=cause_extractor(doc,text)
    final_doc.update(cause_doc)
    method_doc=method_extractor(doc,text)
    final_doc.update(method_doc)
    return final_doc

#text='''BJP's Kapil Mishra criticised those calling for his arrest following his remarks ahead of the violence in North-East Delhi. "Those who did not consider Burhan Wani and Afzal Guru as terrorists, are calling Kapil Mishra a terrorist," Mishra tweeted. "Those who go to court to get Yakub Memon...released are demanding arrest of Kapil Mishra. Jai Shri Ram," he added.'''
#4W_doc=extract_4W(text)

