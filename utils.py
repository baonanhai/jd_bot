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
    rsakey = RSA.importKey(pub_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    result = base64.b64encode(cipher.encrypt(password))
    return result.decode('utf-8')


if __name__ == '__main__':
    password = 'nihao1234'
    key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDC7kw8r6tq43pwApYvkJ5laljaN9BZb21TAIfT/vexbobzH7Q8SUdP5uDPXEBKzOjx2L28y7Xs1d9v3tdPfKI2LR7PAzWBmDMn8riHrDDNpUpJnlAGUqJG9ooPn8j7YNpcxCa1iybOlc2kEhmJn5uwoanQq+CA6agNkqly2H4j6wIDAQAB"
    print(encrypt(password, key))
