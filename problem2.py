from flask import abort, Flask, jsonify, request
from os import urandom
from struct import unpack
from simon import SimonCipher
import json
import urllib2

def randomUint64():
    return unpack("<Q", urandom(8))[0]

def experiment(plaintext, key):
    simon = SimonCipher(key)
    cipher, leak = simon.encrypt(plaintext)

    binary_print(cipher)
    binary_print(leak)

def binary_print(int):
    print('binary={0:0128b}'.format(int))

def binary_print_64(int):
    print('binary={0:064b}'.format(int))

def get_data(num,local):
    #Read JSON data into the datastore variable
    if local:
        url = "http://127.0.0.1:3000/?num="
        contents = urllib2.urlopen(url + str(num)).read()
    else:
        url = "http://6857simon.csail.mit.edu/?num="
        contents = urllib2.urlopen(url + str(num)).read()
    datastore = json.loads(contents)
    return datastore

def sample_z(data , m, rounds_left):
    n = len(data)
    s_n = 0
    for pair in data:
        s_n += pair[1]
    Z = s_n / float(n) 
    t = rounds_left * 128 - 1
    if abs(Z - t/float(2)) < abs(Z - (t/float(2) + 1)):
        return 0
    else:
        return 1

def func_before_xor(word_size, mod_mask, x, y):
    # x = pt1, y = pt2
    ls_1_x = ((x >> (word_size - 1)) + (x << 1)) & mod_mask
    ls_8_x = ((x >> (word_size - 8)) + (x << 8)) & mod_mask
    ls_2_x = ((x >> (word_size - 2)) + (x << 2)) & mod_mask

    # XOR Chain
    xor_1 = (ls_1_x & ls_8_x) ^ y
    xor_2 = xor_1 ^ ls_2_x

    return xor_2

def get_round_key(word_size,data, rounds_left):
    K = [0] * word_size
    for i in range(word_size):
        data_0 = []
        data_1 = []
        for triple in data:
            if '{0:064b}'.format(triple[2])[i] == '0':
                data_0.append(triple)
            else:
                data_1.append(triple)
        if len(data_0) > len(data_1):
            K[i] = sample_z(data_0,i, rounds_left)
        else:
            K[i] = 1 - sample_z(data_1,i, rounds_left)

    K_int = int("".join(str(x) for x in K),2)
    K_binary = ('{0:064b}'.format(K_int))
    print( K_binary)
    return K_int


def main():
    n = 10000
    local = False
    data = get_data(n, local)
    print ("requested packet number " + str(1))
    for i in range(49):
        data = data + get_data(n, local)
        print ("requested packet number " + str(i +2))
    word_size = 64
    mod_mask = (2 ** word_size) - 1

    for pair in data:
        plaintext = pair[0]
        x = (plaintext >> word_size) & mod_mask
        y = plaintext & mod_mask
        pair.append(func_before_xor(word_size, mod_mask, x, y))

    K_1 = get_round_key(word_size,data, 68)

    round_data = []
    for datapoint in data:
        plaintext = datapoint[0]
        x = (plaintext >> word_size) & mod_mask
        y = plaintext & mod_mask
        ct_1 = datapoint[2] ^ K_1
        num_ones = bin(ct_1).count("1") + bin(x).count("1")
        func_result = func_before_xor(word_size, mod_mask, ct_1, x)
        round_data.append([plaintext, datapoint[1] - num_ones, func_result])

    K_2 = get_round_key(word_size,round_data, 67)

    key = (K_2 << 64) + K_1
    binary_print(key)
    print(key)

if __name__ == "__main__":
    main()

