import ast
import json
import re

from collections import Counter
import numpy as np
from pathlib import Path


#from panacea.activeinvestigation.whoisxml import investigate_using_db
#from mysite.settings import STATICFILES_DIRS

mydict = {"Mon,": 1, "Tue,": 2, "Wed,": 3, "Thu,": 4,
              "Fri,": 5, "Sat,": 6, "Sun,": 7}
EN_THRESH = 0.75
MAX_DIST = 100000
MIN_NUM_VALUES = 10
MIN = 0.00001
SUB_THRESH = 4
TOTAL_FEATURES = 15

#static_dir_senderprofile = STATICFILES_DIRS[0] + '/panacea/senderprofile/'


static_dir_senderprofile = 'data/'

def func_convert_HKEY_tolower(HKEY):
    s = str(HKEY).lower()
    return ast.literal_eval(s)

def convert_lower(head):
    head1 = {}
    for _k, _v in head.items():
        lower_k = _k.lower()
        head1[lower_k] = _v
    return head1

def extract_domain(dom_str):
    dom  = 'empty'
    dom_ext = ''
    prefix = dom_str.split('@')
    if len(prefix) > 1:
        dom_ext = prefix[len(prefix) -1 ]
    else:
        dom_ext = dom_str
    dom_parts = dom_ext.split('.')
    #print(dom_parts)
    parts_len = len(dom_parts)
    #print(dom_parts[parts_len-2])
    #print(dom_parts[parts_len-1])
    if len(dom_parts) >= 2:
        dom = dom_parts[parts_len-2] + '.' + dom_parts[parts_len-1]
        #print(dom)
    return dom

def read_time(m):
    if m:
        time = m.group(0)
        zone_time = time.split(' ')[0]
        zone = time.split(' ')[1]
        hour = zone_time.split(':')[0]
        minute = zone_time.split(':')[1]
        second = zone_time.split(':')[2]
        # print( int(zone)/100 )
        universal_time = int(minute) * 60 + int(second) + ((int(hour) - int(zone) / 100)) * 3600
        # print(universal_time)
        return universal_time
    else:
        return 0


def read_address(add, head):
    address = ''
    if add in head:
        item = head[add]
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', item)
        if m:
            address = m.group(0)
        else:
            address = ''
    return address

def read_reply(head):
    reply = 'empty'
    if 'reply-to' in head:
        item = head['reply-to']
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', item)
        if m:
            reply = extract_domain(m.group(0) )
    return reply

def read_domain(head, feature):
    domain = 'empty'
    if feature in head:
        item = head[feature]
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', item)
        if m:
            domain = extract_domain(m.group(0) )
    return domain

def read_domain_no_at(head, feature):
    domain = 'empty'
    if feature in head:
        item = head[feature]
        m = re.search('([a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', item)

        return m.group(0)
    return domain

def read_spf(head):
    spf = 'empty'
    if 'received-spf' in head:
        item = head['received-spf']
        word_list = item.split()
        if len( word_list ) > 0:
            spf = word_list[0]
    return spf.lower().strip()



def rindex(lst, val):
    try:
        return next(len(lst)-i for i, e in enumerate(reversed(lst), start=1) if e == val)
    except StopIteration:
        raise ValueError('{} is not in list'.format(val))



def read_originator(head):
    originator = 'empty'
    if 'received' in head:
        if isinstance(head['received'], list):
            path_len = len(head['received'])
            item = head['received'][path_len - 1].lower()
        else:
            item = head['received'].lower()
        #print('received: ', item)
        word_list = item.split()
        #print(word_list)
        if len( word_list ) > 0:
            if 'by' in word_list:
                index = rindex(word_list, 'by')


                #print(index)
                originator =  extract_domain( word_list[index+1] )
                return originator
            if 'from' in word_list:
                index = rindex(word_list, 'from')
                #print(index)
                originator =  extract_domain( word_list[index+1] )
                #originator =  word_list[index+1]
    #print('originator: ', originator)
    return originator

def read_dmarc(head):
    dmarc = 'empty'
    if 'authentication-results' in head:
        item = head['authentication-results'].lower()
        word_list = item.split()
        for word in word_list:
            if word.startswith('dmarc'):
                equal_parts = word.split("=")
                if len(equal_parts) > 0:
                    dmarc = equal_parts[1]
    if (dmarc == ''):
        dmarc = 'empty'
    return dmarc.strip('\"')

def read_dkim(head):
    dkim = 'empty'
    if 'authentication-results' in head:
        item = head['authentication-results'].lower()
        word_list = item.split()
        for word in word_list:
            if word.startswith('dkim'):
                equal_parts = word.split("=")
                if len(equal_parts) > 1:
                    dkim = equal_parts[1]
    if (dkim == ''):
        dkim = 'empty'
    return dkim.strip().lower()


def read_hour(head):
    send_hour =  'empty'
    date = head['date']
    m1 = re.search('\d{2}:\d{2}:\d{2}', date)
    if m1:
        hour_min_sec = m1[0].split(' ')[0]
        hour = hour_min_sec.split(':')[0]
        ihour = int(hour)
        send_hour = int(ihour/6)
    return send_hour


def read_length(head):
    length = 0
    rec = head['received']
    length = rec.count('Received:')
    return length



def read_vec(header1):
    header = convert_lower(header1)
    feature_list = []
    fromd = read_domain(header,'from')
    originator = read_originator(header)
    #print('originator = ', originator)
    #if check_true_dom(originator) == 0:
        #originator = 'empty'
    returnd = read_domain(header,'return-path')
    replyto = read_domain(header,'reply-to')

    from_originator = '1' if (fromd == originator or originator == 'empty') else '0'
    from_return = '1' if (fromd == returnd or returnd == 'empty') else '0'
    from_replyto = '1' if (fromd == replyto or replyto == 'empty') else '0'
    originator_return = '1' if (originator == returnd or originator == 'empty' or returnd == 'empty') else '0'
    feature_list.append(int(from_originator))
    feature_list.append(int(from_return))
    feature_list.append(int(from_replyto))
    feature_list.append(int(originator_return))

    spf = read_spf(header)
    #print('spf = ', spf)
    spf_pass = '1' if (spf=='pass' or spf=='empty' or spf=='permerror') else '0'


    dmarc = read_dmarc(header)
    dmarc_exist = '1' if (dmarc!='empty') else '0'
    dmarc_pass = '1' if (dmarc.startswith('pass') or dmarc.startswith('none')) else '0'

    dkim = read_dkim(header).lower()
    dkim_pass = '1' if (dkim.startswith('pass') or dkim.startswith('none') ) else '0'

    feature_list.append(int(spf_pass))
    feature_list.append(int(dmarc_exist))
    feature_list.append(int(dmarc_pass))
    feature_list.append(int(dkim_pass))
    feature_list.append(read_sub_char(header))
    feature_list.append(read_sub_len(header))
    return feature_list

def read_sub_char(header):
    if 'subject' in header.keys():
        sub = header['subject']
    else:
        sub =''
    if set('!@#$&').intersection(sub):
        return 0
    else:
        return 1

def read_sub_len(header):
    if 'subject' in header.keys():
        sub = header['subject']
    else:
        sub =''
    if len(sub) >= 6:
        return 1
    else:
        return 0

def read_feature_vec(header):
    feature_list = []
    fromd = read_domain(header,'from')
    originator = read_originator(header)
    returnd = read_domain(header,'return-path')
    replyto = read_domain(header,'reply-to')



    spf = read_spf(header)


    dmarc = read_dmarc(header)
    dkim = read_dkim(header)

    sub_char = read_sub_char(header)
    sub_len = read_sub_len(header)
    return [fromd, originator,  returnd, replyto, spf, dmarc, dkim, sub_char, sub_len]




