
import re

import json
from collections import Counter

import pickle
import read_feature as rf
import sys

sys.stdout = open('b_all10.txt', 'w')

def read_address(add, head):
    address = ''
    if add in head:
        item = head[add]
        #print(item[0])
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', item[0])
        if m:
            address = m.group(0)
        else:
            address = ''
    return address

def load_pickle_from_file(file_name):
    with open(file_name, 'rb') as handle:
        _output = pickle.load(handle)
    return _output

'''
my_dict = {}
if 'test' in my_dict:
    my_dict['test']  += 'dsh'
else:
    my_dict['test']  = 'dsh'
print(my_dict)
m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', 'From Ads Bsds <eqwiuw121_ewiu-+.qe2@gmail.com>')
if m:
    print(m.group(0))
'''



def read_pickle(head_file):
    out = load_pickle_from_file(head_file)
    elist = []
    #for i in range(len(out)):
    for i in range(len(out)):
        #print(out[i])
        from_address = read_address('from', out[i])
        to_address = read_address('to', out[i])
        #print(from_address + " " + to_address)
        if from_address == '' or to_address == '':
            continue
        elist.append(from_address.lower()  + to_address.lower())
    cnt = Counter(elist)
    print(cnt)

def read_pickle_all_key(head_file):
    out = load_pickle_from_file(head_file)
    elist = []
    cn = [0,0,0,0,0,0,0,0, 0,0]
    for i in range(len(out)):
    #for i in range(200):

        for key, value in out[i].items():
            #print (key, value)
            stripped_text = ''
            '''
            for c in value:
                stripped_text += c if len(c.encode(encoding='utf_8'))==1 else ''
            out[i][key] = stripped_text
            '''
            v_str = ''
            for item in value:
                v_str = v_str + item.encode("ascii", "ignore").decode("utf-8")

            out[i][key] = v_str
        #print(rf.read_feature(out[i]))
        #if i== 18840:
            #print(out[i])

        vec = rf.read_vec(out[i])

        #print(vec)
        #print(out[i])
        for j in range(len(vec)):
            print(vec[j], end =" ")
        print('')
        #if vec[5] == 0:
            #print(out[i])
        #for j in range(10):
            #if vec[j] == 1:
                #cn[j] += 1
    #print(len(out))

    #print(cn)

read_pickle_all_key('header_b.pkl')
