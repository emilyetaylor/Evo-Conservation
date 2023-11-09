#!/usr/bin/env python
# coding: utf-8

# In[2]:


from Bio import SeqIO
import sys
#Unix code line : format_fasta_to_tab.py fileIn fileOut 
#Will make new file if output file does not exist

#takes txt file and splits lines by tabs to aqcuire correct info to place into fasta format
#outputs as a new fasta file
out_line = []
temp_line = ''
with open (sys.argv[1], 'r+') as in_f:
    for line in in_f:
            temp_line= line.strip()
            temp_line1= temp_line.split('\t')[0]
            temp_line2= temp_line.split('\t')[1]
            temp_line= '>' +temp_line1+ '\n' +temp_line2
            out_line.append(temp_line)
            
with open(sys.argv[2], 'w') as out_f:
    out_f.write('\n'.join(out_line))
    

