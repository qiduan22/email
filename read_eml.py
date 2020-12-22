#**********************************************************
# Copyright (c) 2020-2021 TTPShield.
# All Rights Reserved.
#**********************************************************

import os
import email
import re
import json
import shutil




def rindex(lst, val):
    try:
        return next(len(lst) - i for i, e in enumerate(reversed(lst), start=1) if e == val)
    except StopIteration:
        raise ValueError('{} is not in list'.format(val))

def extract_domain(dom_str):
    dom = 'empty'
    dom_ext = ''
    prefix = dom_str.split('@')
    if len(prefix) > 1:
        dom_ext = prefix[len(prefix) - 1]
    else:
        dom_ext = dom_str
    dom_parts = dom_ext.split('.')
    # print(dom_parts)
    parts_len = len(dom_parts)
    # print(dom_parts[parts_len-2])
    # print(dom_parts[parts_len-1])
    if len(dom_parts) >= 2:
        dom = dom_parts[parts_len - 2] + '.' + dom_parts[parts_len - 1]
        # print(dom)
    return dom


def extract_add(address):
    add = ''
    start = address.find('<') + 1
    end = address.find('>', start)
    if start > 0:
        add = address[start:end]
    else:
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', address)
        if m:
            add = m.group(0)
    return add

def extract_all_add(address):


    m = re.findall('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', address)
    if m:
        return m
    else:
        return []

def read_originator(head):
    originator = 'empty'
    if 'received' in head:
        item = head['received'].lower()
        word_list = item.split()
        #print(word_list)
        if len( word_list ) > 0:
            if 'from' in word_list:
                index = rindex(word_list, 'from')
                originator =  extract_domain( word_list[index+1] )
                #originator =  word_list[index+1]

    return originator

def check_start_insert(line):

    if  line.startswith('External'):
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', line)
        if m:
            return 1
    if  line.startswith('Report This Email') and 'https://' in line:

        return 1
    #if  line.startswith('External'):
    return 0

def check_end_insert(line):

    if  line == '' or line== '\n' or line =='\r\n':
            return 1
    #if  line.startswith('External'):
    return 0

def check_quote(line):
    if  ((line.startswith('On') or line.startswith('>') ) and line.endswith('wrote:')) or line.startswith('Begin forwarded message:'):
        return 1
    if  line.startswith('From:'):
        m = re.search('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', line)
        if m:
            return 1
    return 0

def store_data(workspace_path, email_dict, to_add):
    folder_names = ['AddedAuthors', 'AuthorsData', 'AuthorsToAdd', 'Header', 'Reference']
    ref_folders= ['salute', 'signature', 'tfidf']
    for name in folder_names:
        if not os.path.exists(workspace_path+name):
            os.makedirs(workspace_path+name)
    for name in ref_folders:
        if not os.path.exists(workspace_path+'Reference/' + name):
            os.makedirs(workspace_path+'Reference/' + name)
    header_file = open(workspace_path+'Header/head.json', 'w')
    head_list = []
    for _k, _v in email_dict.items():
        if _k.lower() == to_add.lower():
            for __k, __v in _v.items():
                author_file = open(workspace_path+'AuthorsToAdd/' + __k.lower()+'.txt', 'w')
                ref_file1 = open(workspace_path+'Reference/salute/' + __k.lower()+'.txt', 'w')
                ref_file2 = open(workspace_path+'Reference/signature/' + __k.lower()+'.txt', 'w')
                ref_file3 = open(workspace_path+'Reference/tfidf/' + __k.lower()+'.txt', 'w')

                for item in __v:
                    if item['original_body'] != '':
                        author_file.write(item['original_body'])
                        author_file.write('===***===\n')
                        ref_file1.write(item['original_body'])
                        ref_file1.write('===***===\n')
                        ref_file2.write(item['original_body'])
                        ref_file3.write(item['original_body'])
                        ref_file3.write('===***===\n')

                    head_list.append(item['head'])

    json.dump({'headers' : head_list}, header_file)


    return 0

def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copyfile(src, dest)



def read_eml_from_dir():
    count = 0
    email_dict = {}
    to_add = input("Please input protected user email address:")
    to_add = to_add.lower()
    from_list_text = input("Please input sender email addresses (minimum 2, separated by ','):")
    from_list_text = from_list_text.lower()
    from_list = from_list_text.split(',')
    for i in range(len(from_list)):
        from_list[i] = from_list[i].strip()

    if to_add not in email_dict.keys():
        email_dict[to_add] = {}
    for from_add in from_list:
        if from_add not in email_dict[to_add].keys():
            email_dict[to_add][from_add] = []

    emails_path = input("Please input emails directory path:")
    if (not (emails_path[len(emails_path) - 1] == '\\' or emails_path[
        len(emails_path) - 1] == '/')):
        emails_path = emails_path + "/"
    minimum_msg_size = 20
    for filename in os.listdir(emails_path):
        count += 1
        with open(os.path.join(emails_path, filename), 'r') as f:
            #print('**************************************')
            msg = email.message_from_file(f)


            parser = email.parser.HeaderParser()
            headers = parser.parsestr(msg.as_string())

            for _k, _v in headers.items():
                #if _k.lower() == 'from' or _k.lower() == 'to' or _k.lower() == 'date':
                    #print(_k, _v)
                if _k.lower() == 'from':
                    from_add_current = extract_add(_v.lower())
                if _k.lower() == 'to':
                    to_add_current = extract_all_add(_v.lower())


            if to_add in to_add_current  and from_add_current in from_list:

                '''
                if msg.is_multipart():
                    for part in msg.walk():
                        payload = part.get_payload(decode=True) #returns a bytes object
                        if payload:
                            strtext = payload.decode('utf-8','ignore') #utf-8 is default
                            print(strtext)
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        strtext = payload.decode('utf-8','ignore')
                        print(strtext)
                '''
                bodytext = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body = part.get_payload(decode=True)  # decode
                            break
                else:
                    body = msg.get_payload(decode=True)
                original_body = ''
                quote = ''
                if body:
                    bodytext = body.decode('utf-8','ignore')
                    #print(strtext)

                    #email_dict[from_add][to_add]['body'] = strtext
                    bodylines = bodytext.splitlines()
                    is_quote = 0
                    start_insert = 0
                    end_insert = 0
                    for line in bodylines:
                        line_no_unicode = re.sub(r'[^\x00-\x7F]',' ', line)
                        if end_insert == 0:
                            if start_insert == 0 and check_start_insert(line_no_unicode) == 1:
                                start_insert = 1
                                original_body = ''
                                continue
                            if start_insert == 1 and check_end_insert(line_no_unicode) == 1:
                                end_insert = 1
                                start_insert = 0
                                continue
                        if start_insert != 1:
                            if is_quote == 0:
                                is_quote = check_quote(line_no_unicode)
                            if is_quote == 1:

                                quote = quote + line_no_unicode + '\n'
                                continue

                            original_body = original_body +  line_no_unicode + '\n'



                org_body_words = original_body.split()
                if len(org_body_words) < minimum_msg_size:
                    original_body = ''
                head = {}
                for _k, _v in headers.items():
                    if _k != 'Received':
                        head[_k] = _v
                    else:
                        if 'Received' not in head.keys():
                            head['Received'] = []

                        head['Received'].append(_v)
                email_head_body ={'head': head, 'original_body': original_body, 'quote':quote}
                email_dict[to_add][from_add_current].append(email_head_body)
                #print(bodytext)
    #print(email_dict)
    with open('emails.json', 'w') as fp:
        json.dump(email_dict, fp)
    print('Specified emails saved in file emails.json')


#print(count)

def read_single_email(email_file):
    with open(email_file, 'r') as f:
        #print('**************************************')
        msg = email.message_from_file(f)


        parser = email.parser.HeaderParser()
        headers = parser.parsestr(msg.as_string())

        #for _k, _v in headers.items():
        #    #if _k.lower() == 'from' or _k.lower() == 'to' or _k.lower() == 'date':
        #        #print(_k, _v)
        #    if _k.lower() == 'from':
        #        from_add_current = extract_add(_v.lower())
        #    if _k.lower() == 'to':
        #        to_add_current = extract_all_add(_v.lower())

        #if to_add in to_add_current  and from_add_current in from_list:
        '''
        if msg.is_multipart():
              for part in msg.walk():
                 payload = part.get_payload(decode=True) #returns a bytes object
                 if payload:
                    strtext = payload.decode('utf-8','ignore') #utf-8 is default
                    print(strtext)
        else:
              payload = msg.get_payload(decode=True)
              if payload:
                 strtext = payload.decode('utf-8','ignore')
                 print(strtext)
        '''
        bodytext = ''
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)  # decode
                    break
        else:
            body = msg.get_payload(decode=True)
        original_body = ''
        quote = ''
        if body:
            bodytext = body.decode('utf-8','ignore')
            #print(strtext)

            #email_dict[from_add][to_add]['body'] = strtext
            bodylines = bodytext.splitlines()
            is_quote = 0
            start_insert = 0
            end_insert = 0
            for line in bodylines:
                line_no_unicode = re.sub(r'[^\x00-\x7F]',' ', line)
                if end_insert == 0:
                    if start_insert == 0 and check_start_insert(line_no_unicode) == 1:
                        start_insert = 1
                        original_body = ''
                        continue
                    if start_insert == 1 and check_end_insert(line_no_unicode) == 1:
                        end_insert = 1
                        start_insert = 0
                        continue
                if start_insert != 1:
                    if is_quote == 0:
                        is_quote = check_quote(line_no_unicode)
                    if is_quote == 1:

                        quote = quote + line_no_unicode + '\n'
                        continue

                    original_body = original_body +  line_no_unicode + '\n'



        head = {}
        for _k,_v in headers.items():
            if _k != 'Received':
                head[_k] = _v
            else:
                if 'Received' not in head.keys():
                    head['Received'] = []

                head['Received'].append(_v)
        email_head_body ={'head': head, 'original_body': original_body, 'quote':quote}
        return email_head_body

def modify_email_file_with_result(result, email_file):
#	content="X-header_classification: "+result['header_classification']+", header_score: "+result['header_score']+\
#	", profile_classification: "+result['profile_classification']+", profile_score: "+result['profile_score']+\
#	", content_sender: "+result['content_sender']+", content_unknown: "+result['content_unknown']
	res_line = ""
	res_line = res_line+"X-header_classification: "+str(result['header_classification']) +"\n"
	res_line = res_line+"X-header_score: "+str(result['header_score']) +"\n"
	res_line = res_line+"X-profile_classification: "+str(result['profile_classification']) +"\n"
	res_line = res_line+"X-profile_score: "+str(result['profile_score']) +"\n"
	res_line = res_line+"X-content_sender: "+str(result['content_sender']) +"\n"
	res_line = res_line+"X-content_unknown: "+str(result['content_unknown'])
	with open(email_file, 'r+') as f:
		content = f.read()
		f.seek(0, 0)
		f.write(res_line.rstrip('\r\n') + '\n' + content)
if __name__ == '__main__':
    read_eml_from_dir()

