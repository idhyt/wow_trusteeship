#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time


_CERT_KEY = "M.jiEp[+*Ay0b^p"


def get_sign_key(salt, v):
    import hmac
    if isinstance(v, str):
        sign_byte = v.encode("utf-8")
    else:
        sign_byte = v

    return hmac.new(salt.encode("utf-8"), sign_byte, 'sha1').hexdigest()


def get_period_token(key=_CERT_KEY, expired=1, payload=""):
    """
    :param key:
    :param expired: period of validity, minutes.
    :param payload
    :return:
    """
    import base64
    ts_str = str(time.time() + expired * 60)
    sign_str = "{}:{}".format(ts_str, str(payload))
    token = "{expired}:{sha1_key}:{payload}".format(
        expired=ts_str,
        sha1_key=get_sign_key(key, sign_str),
        payload=payload
    )
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


li_exp = 600
li_pl = "landatou"


def main():

    lk = get_period_token(expired=li_exp, payload=li_pl)
    info = "licence: {}\nexpired: {} minutes, info: {}".format(lk, li_exp, li_pl)
    print(info)


if __name__ == '__main__':
    main()
