# 6.857 Spring 2018 Problem Set 1
# sfraser@mit.edu, 02/26/2018

### Question 1-2. Re-Using a One-Time Pad ###

import nltk
import string

#lower case set of all possible words in English
english_vocab = set(w.lower() for w in nltk.corpus.words.words())

### Part (a) ###

print("\n ===== Problem 2a ===== \n")

word_length = 12
possible_words = set()

for word in english_vocab:
    if len(word) == word_length:
        possible_words.add(word)

a = ['a6', 'a5', '6d', 'f4', '8c', 'a0', 'fc', '86', 'd6', '1f', '2f', 'e9']
b = ['ac', 'b9', '60', 'e1', '94', 'a3', 'f2', '93', 'd2', '01', '24', 'f5']

def xor_lists_byte_strings(a,b):
    xored = []
    for i in zip(a,b):
        xored.append(int(i[0], 16) ^ int(i[1],16))
    return xored

c1_xor_c2 = xor_lists_byte_strings(a,b)

print ("Possible Word Combinations:")
# find m1 xor'ed with c1 xor c_2, and check if the result is a m2 in the possible word set
for m1 in possible_words:
    m1_as_int = [ord(c) for c in m1]
    m2_as_int = []
    for i in zip(c1_xor_c2, m1_as_int):
        m2_as_int.append(i[0] ^ i[1])
    m2 = ''.join([chr(i) for i in m2_as_int])
    if m2 in possible_words:
        print (m1,m2)

### Part (d) ###

print("\n ===== Problem 2d ===== \n")

g = {}

#helper dictionary to help index g table/function
hex_dict = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}

#create g function dictionary lookup table
with open('gbox.txt') as f:
    row = 0
    col = 0
    for line in f:
        col = 0
        for char in line.split():
            g[hex_dict[row]+hex_dict[col]] = char
            col += 1
        row += 1

#compute inverse table for inverse g function
inv_g = {v: k for k, v in g.items()}

#the 100 printable ASCII characters
printable_characters = set(string.printable)


# finds the pads for the given problem, in this case there was only one possible pad with the constraints
def find_pads(printable_characters, g, inv_g):
    pad_length = 0
    # get length of pad/ messages
    with open('10ciphs.txt') as f:
        for line in f:
            pad_length = len(line.split())

    pad_list_int = []
    for i in range(pad_length):
        possible_pad_i = set(range(2**8))
        with open('10ciphs.txt') as f:
            for line in f:
                char_list = line.split()
                c = char_list[i]
                if (i == 0):
                    prev_c = '00'
                else:
                    prev_c = char_list[i-1]
                pads_to_remove = set()
                for p in possible_pad_i:
                    # perform reverse of calculation in 2b
                    key = format(int(c,16) ^ p, '02x')
                    char = chr(int(inv_g[key],16)^ int(prev_c,16))
                    if char not in printable_characters:
                        pads_to_remove.add(p)
                    else:
                        continue
                possible_pad_i = possible_pad_i.difference(pads_to_remove)
                if len(possible_pad_i) == 1:
                    pad_list_int.append(max(possible_pad_i))
                    prev_c = c
                    break
                prev_c = c

    return pad_list_int

pad_list_int = find_pads(printable_characters, g, inv_g)

lines = []
with open('10ciphs.txt') as f:
    for line in f:
        lines.append(line.split())

print ("Pad used:")
pad = [format(i,'02x') for i in pad_list_int]
out = ''
for i in pad:
    out += i
    out += ' '
print(out[:-1])

#Decryption of the message
print ("\nDecrypted Message:\n")
for c in lines:
    msg_length = len(c)
    msg = ''
    for i in range(msg_length):
        if i == 0:
            prev_c = '00'
        else:
            prev_c = c[i-1]
        # decryption - same process as in 2b
        key = format(int(c[i],16) ^ pad_list_int[i], '02x')
        char = chr(int(inv_g[key],16)^ int(prev_c,16))
        msg += char
    print(msg)
