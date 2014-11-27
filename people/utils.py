# -*- coding:utf-8 -*-
import datetime
from common.utils import photo_cut, user_send_xmpp, photo_to_dict
from django.conf import settings

def get_zodiac(date):
    month = date.month
    day = date.day
    zodiac_map = {
        u'白羊座':[(3,21), (4,20)],
        u'金牛座':[(4,21), (5,20)],
        u'双子座':[(5,21), (6,21)],
        u'巨蟹座':[(6,22), (7,22)],
        u'狮子座':[(7,23), (8,22)],
        u'处女座':[(8,23), (9,22)],
        u'天秤座':[(9,23), (10,22)],
        u'天蝎座':[(10,23), (11,21)],
        u'射手座':[(11,23), (12,22)],
        u'水瓶座':[(1,20), (2,18)],
        u'双鱼座':[(2,19), (3,20)]
    }
    for k,v in zodiac_map.iteritems():
        if v[0] <= (month,day) <= v[1]:
            return k

    if (month,day) >= (12,22) or (month,day) <= (1,19):
        return u'摩羯座'


