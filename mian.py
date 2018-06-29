import random

import requests
from bs4 import BeautifulSoup

from config import jd_user, jd_password, jd_eid, jd_fp
from utils import encrypt


class JDSdK(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        self.req = requests.session()

    def login(self):
        resp = self.req_get('https://passport.jd.com/uc/login')
        soup = BeautifulSoup(resp.text, 'lxml')
        sa_token = soup.find(id="sa_token")['value']
        uuid = soup.find(id="uuid")['value']
        _t = soup.find(id="token")['value']
        login_type = soup.find(id="loginType")['value']
        pub_key = soup.find(id="pubKey")['value']
        password = encrypt(self.password, pub_key)
        data = {'uuid': uuid, 'eid': jd_eid, 'fp': jd_fp, '_t': _t, 'loginType': login_type, 'loginname': self.user,
                'nloginpwd': password, 'authcode': '', 'pubKey': pub_key, 'sa_token': sa_token}
        self.headers['Host'] = 'passport.jd.com'
        self.headers['Origin'] = 'https://passport.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/uc/login'
        resp = self.req_post(f'https://passport.jd.com/uc/loginService?uuid={uuid}&version=2015&r={random.random()}',
                             data)
        print(resp.text)

    def req_get(self, url, params=None):
        if params:
            resp = self.req.post(url, params=params, headers=self.headers, timeout=10)
        else:
            resp = self.req.post(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp

    def req_post(self, url, data):
        resp = self.req.post(url, data=data, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp


if __name__ == '__main__':
    jd_sdk = JDSdK(jd_user, jd_password)
    jd_sdk.login()
