import mailbox
import email
import json
import re
import dateutil.parser
from read_content import extract_add, extract_all_add, check_start_insert, check_end_insert, check_quote

def read_date(date):

    return dateutil.parser.parse(date)

def extract_date(date_str):
    date_list = []
    if '-' in date_str:
        date_list = date_str.split('-')
    if '/' in date_str:
        date_list = date_str.split('/')
    return date_list

def compare_date(d1, d2):
    d1_list = extract_date(d1)
    d2_list = extract_date(d2)
    if d1_list[0] > d2_list[2]:
        return 1
    elif d1_list[0] < d2_list[2]:
        return 0
    else:
        if d1_list[1] > d2_list[0]:
            return 1
        elif d1_list[1] < d2_list[0]:
            return 0
        else:
            if d1_list[2] >= d2_list[1]:
                return 1
            else:
                return 0


def read_mb():
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
    from_date = input("Please input starting date (in mm/dd/yyyy):")
    end_date = input("Please input ending date (in mm/dd/yyyy):")
    subject_string = input("Please input subject string:")
    filename = input("Please input mbox file name:")

    for msg in mailbox.mbox(filename):
        count += 1
        parser = email.parser.HeaderParser()
        msg_str = msg.as_bytes()
        #print(msg_str)
        msg_str_ascii =  msg_str.decode('ascii', errors='ignore')
        headers = parser.parsestr(msg_str_ascii)
        sub_no_match = 0
        not_range = 0
        #print('date: ', date_string)
        for _k, _v in headers.items():
            #if _k.lower() == 'from' or _k.lower() == 'to' or _k.lower() == 'date':
                #print(_k, _v)
            if _k.lower() == 'from':
                from_add_current = extract_add(_v.lower())
            if _k.lower() == 'to':
                to_add_current = extract_all_add(_v.lower())
                #print(to_add_current)
            if _k.lower() == 'date':
                date_string = str(read_date(_v))[0:10]
                if compare_date(date_string, from_date) == 0 or compare_date(date_string, end_date) == 1:
                    #print('date: ', date_string)
                    not_range = 1
            if _k.lower() == 'subject':
                if subject_string.lower() not in _v.lower():

                    #print('subject: ', _v)
                    sub_no_match = 1
        #print('from_list: ', from_list)
        #print('to_add: ', to_add)

        #if not_range == 0 and sub_no_match == 0:
            #print('sub: ', headers['Subject'])
            #print('date: ', date_string)
            #print('from_add_current: ', from_add_current)

            #print('to_add_current: ', to_add_current)

        if to_add in to_add_current  and from_add_current in from_list and not_range == 0 and sub_no_match == 0:
            #print('find')
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
            if len(org_body_words) < 20:
                original_body = ''
            if original_body.startswith('<') :
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
            #print(email_dict)
                #print(bodytext)
    #print('first sender wfcarson01@gmail.com')
    #print(email_dict['mark@cyberrr.com'])
    #print('Second sender wfcarson01@gmail.com')
    #print(email_dict['mark@cyberrr.com']['bill.carson@princetonirtech.com'])
    with open('emails_mbox.json', 'w') as fp:
        json.dump(email_dict, fp)

    print('The specified emails are saved to file emails_mbox.json')

if __name__ == '__main__':

    read_mb()
