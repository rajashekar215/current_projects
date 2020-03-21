# -*- coding: utf-8 -*-
import json
from nltk import tokenize
import time
from pre_tags_telugu import *
import re
# =============================================================================
# with open("emission_matrix.json", "r") as read_file:
#         emission_matrix=json.load(read_file)
# with open("transmission_matrix.json", "r") as read_file:
#         transmission_matrix=json.load(read_file)
# 
# =============================================================================
tags = ['NN', 'NST', 'NNP', 'PRP', 'DEM', 'VM', 'VAUX', 'JJ', 'RB', 'PSP', 'RP', 'CC', 'WQ', 'QF', 'QC', 'QO', 'CL', 'INTF', 'INJ', 'NEG', 'UT', 'SYM', 'COMP', 'RDP', 'ECH', 'UNK', 'XC','NNO','SYMP',u'NNP\u200c',u'NNP_ORG', u'NN_ORG', u'NN_O', u'VM_O', u'NST_O', u'NNP_PERSON', u'PSP_O', u'DEM_O', u'SYM_O', u'QC_MISC', u'WQ_O', u'RB_O', u'NNP_LOC', u'UT_O', u'PRP_O', u'CL_O', u'NNP_O', u'JJ_O', u'QF_O', u'NN_MISC', u'QO_MISC', u'INTF_O', u'CC_O', u'RP_O', u'QC_O', u'NNP_MISC', u'NN_PERSON', u'RB_MISC', u'NN_LOC', u'VM_PERSON', u'JJ_MISC', u'NNO_PERSON', u'VM_ORG', u'SYMP_O', u'VM_MISC',u'NNP_B-ORG', u'NN_I-ORG', u'NNP_I-ORG', u'NNP_B-PERSON', u'QC_B-MISC', u'NNP_B-LOC', u'NNP_I-PERSON', u'NN_B-ORG', u'NN_B-MISC', u'QC_I-MISC', u'QO_B-MISC', u'NN_I-MISC', u'NNP_I-LOC', u'NNP_B-MISC', u'NN_I-PERSON', u'NN_B-PERSON', u'RB_B-MISC', u'NN_B-LOC', u'VM_I-PERSON', u'RB_I-MISC', u'JJ_B-MISC', u'NNO_B-PERSON', u'VM_I-ORG', u'VM_B-MISC']

def max_connect(x, y, viterbi_matrix, emission, transmission_matrix):
    max = -99999
    path = -1
    
    for k in range(len(tags)):
        val = viterbi_matrix[k][x-1] * transmission_matrix[k][y]
        if val * emission > max:
            max = val
            path = k
    return max, path

#@staticmethod
def tag(input_sentence):
    start_time = time.time()

    # Open the testing file to read test sentences
    #testpath = sys.argv[2]
    #file_test = codecs.open(testpath, 'r', encoding='utf-8')
    test_input = tokenize.sent_tokenize(input_sentence)
    # Declare variables for test words and pos tags
    tag_output = []
    test_words = []
    pos_tags = []

    # Create an output file to write the output tags for each sentences
    #file_output = codecs.open("./output/"+ languages[int(sys.argv[1])] +"_tags.txt", 'w', 'utf-8')
    #file_output.close()

    # For each line POS tags are computed
    for j in range(len(test_input)):
        
        test_words = []
        pos_tags = []

        line = test_input.pop(0).strip().split(' ')
        
        new_doc=[]
        for w in line:
            w=re.sub('\s*\d*\s', '', w)
            if re.search('(\r\n|\n|\r|\s|\.$|^\.|^,|,$|^\'|\'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$|^#|#$|^\;|\;$|^\d|\d$|^\*|\*$|^-|-$|^\(|\)$|^\/|\/$)',w):
#                         print("wordddd",w)
                        try:
                            start = re.search('(^[\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*)',w).group()
#                             print("start",start)
                            w = w.replace(start,"")
                        except:
                            pass
                        try:
                            end = re.search('([\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*$)',w).group()
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
                    middle = re.search('[^\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]*([\.,\'\":\?<>&\r\n\n#\s\d\;\*\-\!\(\)\/]+).*',w).groups()[0]
#                     print("middle  ",middle)
                    w = w.replace(middle," ")
                    w=w.split(" ")
#                     print("split  ",w)
                    if w is not "":
                        new_doc.extend(w)
                except:
                    new_doc.append(w)
            
        
        for word in new_doc:
            word=word.rstrip(".")
            test_words.append(word)
            pos_tags.append(-1)

        viterbi_matrix = []
        viterbi_path = []
        
        # Initialize viterbi matrix of size |tags| * |no of words in test sentence|
        for x in range(len(tags)):
            viterbi_matrix.append([])
            viterbi_path.append([])
            for y in range(len(test_words)):
                viterbi_matrix[x].append(0)
                viterbi_path[x].append(0)

        # Update viterbi matrix column wise
        for x in range(len(test_words)):
            for y in range(len(tags)):
                if test_words[x] in wordtypes:
                    word_index = wordtypes.index(test_words[x])
                    tag_index = tags.index(tags[y])
                    emission = emission_matrix[tag_index][word_index]
                else:
                    emission = 0.001

                if x > 0:
                    max, viterbi_path[y][x] = max_connect(x, y, viterbi_matrix, emission, transmission_matrix)
                else:
                    max = 1
                viterbi_matrix[y][x] = emission * max

        # Identify the max probability in last column i.e. best tag for last word in test sentence
        maxval = -999999
        maxs = -1
        for x in range(len(tags)):
            if viterbi_matrix[x][len(test_words)-1] > maxval:
                maxval = viterbi_matrix[x][len(test_words)-1]
                maxs = x
            
        # Backtrack and identify best tags for each words
        for x in range(len(test_words)-1, -1, -1):
            pos_tags[x] = maxs
            maxs = viterbi_path[maxs][x]

        # Display POS Tags in the console.
        # print(pos_tags)
        
        # Print output to the file.    
        
        for i, x in enumerate(pos_tags):
            tag_output.append({"word":test_words[i],"tag":tags[x]})
            

    #print(tag_output)
    #print(time.time() - start_time, "seconds for tagging")
    return tag_output
    
    
    
    
# =============================================================================
# with open("golden_telugu_data.txt", "a+") as write_file:
#     with open("test_sentences_9_IOB.txt", "r+") as read_file:
#         d=read_file.readlines() 
#         for l in d:
#             write_file.write(l)
# =============================================================================

