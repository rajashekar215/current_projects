# -*- coding: utf-8 -*-
from gtranslate import *
import time

input_file=open("english_words",newline="\n").readlines()

output_file=open("telugu_words","a+")
output_file_length=len(output_file.readlines())
print("output file length:: ",output_file_length)

s=0
for w in range(output_file_length,len(input_file)):
    try:
        tw=trns(input_file[w])
        #print(tw)
        output_file.write(tw+"\n")
# =============================================================================
#         s=s+1
#         if s<10:
#             time.sleep(2)
#         if s==10:
#             s=0
#             time.sleep(15)
# =============================================================================
    except Exception as e:
        print(e)
        break

output_file.close()