
import os
import email

if __name__ == '__main__':
    sender_dict = {}
    for filename in os.listdir('email'):

        with open(os.path.join('email', filename), 'r') as f:
            #print(filename)
            msg = email.message_from_file(f)


            parser = email.parser.HeaderParser()
            header = parser.parsestr(msg.as_string())


            sender = header['From'].lower()
            if sender not in sender_dict.keys():
                sender_dict[sender] = 1
            else:
                sender_dict[sender] += 1

    sorted_tuple = sorted(sender_dict.items(), key=lambda x:x[1], reverse = True )
    print(sorted_tuple)


