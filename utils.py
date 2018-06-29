#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import base64

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def format_key(pub_key):
    result = '-----BEGIN PUBLIC KEY-----\n'
    for i in range(4):
        result += pub_key[64 * i: 64 * (i + 1)]
        result += '\n'
    result += '-----END PUBLIC KEY-----\n'
    return result


def encrypt(password: str, pub_key: str):
    password = password.encode('utf-8')
    pub_key = format_key(pub_key)
    rsa_key = RSA.importKey(pub_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    result = base64.b64encode(cipher.encrypt(password))
    return result.decode('utf-8')


def load_test_data(path):
    data = ''
    with open(path, 'r') as test:
        for line in test:
            data += line
    return data
