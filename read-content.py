import os
import email

count = 0

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

for filename in os.listdir('email'):
    count += 1
    with open(os.path.join('email', filename), 'r') as f:
        print('**************************************')
        msg = email.message_from_file(f)


        parser = email.parser.HeaderParser()
        headers = parser.parsestr(msg.as_string())


        for _k, _v in headers.items():
            if _k.lower() == 'from' or _k.lower() == 'to' or _k.lower() == 'date':
                print(_k, _v)
        if msg.is_multipart():
            for part in msg.walk():
                payload = part.get_payload(decode=True) #returns a bytes object
                if payload:
                    strtext = payload.decode() #utf-8 is default
                    print(strtext)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                strtext = payload.decode()
                print(strtext)

#print(count)

