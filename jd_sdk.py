#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import random
import time

import requests
from PIL import Image
from bs4 import BeautifulSoup, element

from config import jd_eid, jd_fp
from utils import encrypt


class JDCoupon(object):
    def __init__(self, info):
        self.id = info.get('id')[4:]
        self.num = info.find("strong", {"class": "num"}).text
        self.em = info.find("em").text
        self.coupon_type = info.find("div", {"class": "typ-txt"}).text.strip()
        self.price_limit = info.find("span", {"class": "ftx-06"}).text.strip()
        self.range_limit = []
        range_limit_list = info.findAll("div", {"class": "range-item"})
        for range_limit in range_limit_list:
            self.range_limit.append(range_limit.text.strip())


class JDSdK(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        self.req = requests.session()
        self.cache_path = 'cache'
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def login(self):
        resp = self._req_get('https://passport.jd.com/new/login.aspx')
        soup = BeautifulSoup(resp.text, 'lxml')
        auto_code = ''
        if self._is_need_auth_code():
            img = soup.find(id='JD_Verification1')['src2']
            img_url = f'https:{img}&yys={int(time.time()*1000)}'
            auth_code_path = os.path.join(self.cache_path, 'auth_code.jpg')
            self._save_auth_code(img_url, auth_code_path)
            Image.open(auth_code_path).show()
            auto_code = input('请输入验证码:')

        sa_token = soup.find(id="sa_token")['value']
        uuid = soup.find(id="uuid")['value']
        _t = soup.find(id="token")['value']
        login_type = soup.find(id="loginType")['value']
        pub_key = soup.find(id="pubKey")['value']
        password = encrypt(self.password, pub_key)
        data = {'uuid': uuid, 'eid': jd_eid, 'fp': jd_fp, '_t': _t, 'loginType': login_type, 'loginname': self.user,
                'nloginpwd': password, 'authcode': auto_code, 'pubKey': pub_key, 'sa_token': sa_token}
        self.headers['Host'] = 'passport.jd.com'
        self.headers['Origin'] = 'https://passport.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'
        resp = self._req_post(f'https://passport.jd.com/uc/loginService?uuid={uuid}&version=2015&r={random.random()}',
                              data)
        resp = self._get_resp_json(resp)
        if 'success' in resp.keys():
            logging.info('Login successful!')
            return True
        logging.error(f'Err login failed and msg:{resp}')
        return False

    def get_vip_coupon_list(self):
        result = []
        self.headers['Host'] = 'a.jd.com'
        self.headers.pop('Origin')
        self.headers['Referer'] = 'https://a.jd.com/'
        resp = self._req_get('https://a.jd.com/specials.html')
        resp = resp.text
        soup = BeautifulSoup(resp, 'lxml')
        coupon_list = soup.find_all("div", {"class": "quan-item quan-d-item"})
        if not coupon_list:
            logging.warning('Vip coupon get empty')
            return result

        for coupon in coupon_list:
            if not isinstance(coupon, element.Tag):
                continue
            result.append(JDCoupon(coupon))
        return result

    def get_vip_coupon(self, coupon_id):
        self.headers['Host'] = 'a.jd.com'
        self.headers.pop('Origin', None)
        self.headers['Referer'] = 'https://a.jd.com/specials.html'
        data = {'id': coupon_id}
        self._req_post('https://a.jd.com/specials/getVip.html', data=data)

    def _is_need_auth_code(self):
        data = {'loginName': self.user}
        self.headers['Host'] = 'passport.jd.com'
        self.headers['Origin'] = 'https://passport.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'
        resp = self._req_post(f'https://passport.jd.com/uc/showAuthCode?r={random.random()}&version=2015', data=data)
        resp = self._get_resp_json(resp)
        if resp['verifycode']:
            logging.warning('Login need auth code!')
        return resp['verifycode']

    def _save_auth_code(self, img_url, auth_code_path):
        self.headers['Host'] = 'authcode.jd.com'
        self.headers.pop('Origin')
        ir = self._req_get(img_url)
        open(auth_code_path, 'wb').write(ir.content)

    def _req_get(self, url, params=None):
        if params:
            resp = self.req.post(url, params=params, headers=self.headers, timeout=10)
        else:
            resp = self.req.post(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp

    def _req_post(self, url, data):
        resp = self.req.post(url, data=data, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp

    @staticmethod
    def _get_resp_json(resp):
        resp = resp.text
        return json.loads(resp[1:len(resp) - 1])
