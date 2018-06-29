#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import logging

from config import jd_user, jd_password
from jd_sdk import JDSdK

jd_sdk = JDSdK(jd_user, jd_password)


def get_all_owner_vip_coupon():
    """获取所有的vip专属优惠券"""
    jd_sdk.login()
    coupon_list = jd_sdk.get_vip_coupon_list()
    for coupon in coupon_list:
        jd_sdk.get_vip_coupon(coupon.id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    get_all_owner_vip_coupon()
