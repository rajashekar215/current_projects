# -*- coding: utf-8 -*-
from collections import defaultdict
from collections import Counter

length=int(input())
A=input()

char_dict=defaultdict(list)

for index,value in enumerate(A):
    char_dict[value].append(index)

            
solution=0    
for value in A:
    index=char_dict[value].pop(0)
    if len(char_dict[value])>0 and index+1<=length-1 and char_dict[value][0]<=length-1:
        #print(index+1,char_dict[value][0])
        temp_solution=None
        start=index+1
        for iindex,end in enumerate(char_dict[value]):            
            refdict=Counter(A[start:end])
            start=end
            if iindex+1<len(char_dict[value]):
                cmpdict=Counter(A[start:char_dict[value][iindex+1]])
            else:
                cmpdict=Counter(A[start:])
            if len(refdict)>0 and len(cmpdict):
                for key,ivalue in refdict.items():
                    if key in cmpdict:
                        if temp_solution:
                            temp_solution=temp_solution*ivalue*cmpdict[key]
                        else:
                            temp_solution=ivalue*cmpdict[key]
        if temp_solution:
            solution+=temp_solution
                
print(solution)    



solution=0    
for value in A:
    index=char_dict[value].pop(0)
    if len(char_dict[value])>0 and index+1<=length-1 and char_dict[value][0]<=length-1:
        #print(index+1,char_dict[value][0])
        for end in char_dict[value]:
            for key,ivalue in Counter(A[index+1:end]).items():
                #print(A[index+1:char_dict[value][0]])
                #char_dict[ivalue].pop(0)
                #if len(char_dict[ivalue])>0:
                if len(char_dict[key])>0:
                    out=0
                    for i,v in  enumerate(char_dict[key]):
                        if v>end:
                            out=len(char_dict[key][i:])
                            break
                    solution=solution+out*ivalue
                

print(solution)  

