# -*- coding:utf-8 -*-

from django.conf import settings
import binascii
from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSAlert
from apns import APNs, Payload
from django.http import HttpResponse
from multiprocessing import Pool
from datetime import date
import datetime
import threading
import time
import jpush as jpush

def send_new_photo_notification(regids, data):
	_jpush = jpush.JPush(settings.JPUSH_APP_KEY, settings.JPUSH_APP_MASTER)

	push = _jpush.create_push()
	push.audience = jpush.registration_id(*regids)
	push.notification = jpush.notification(ios=jpush.ios(alert='', content_available=True, extras={"d": data, "action": "photo"}))
	push.options = dict(apns_production=False)

	push.platform = jpush.platform('ios')
	return push.send()

def send_friend_notification(regid, data):
	_jpush = jpush.JPush(settings.JPUSH_APP_KEY, settings.JPUSH_APP_MASTER)

	push = _jpush.create_push()
	push.audience = jpush.registration_id(regid)
	push.notification = jpush.notification(ios=jpush.ios(alert='sb has make friend with you!', extras={"d": data, "action": "friend"}))
	push.options = dict(apns_production=False)

	push.platform = jpush.platform('ios')
	return push.send()

def send_like_notification(regid, like_num):
	if not regid or len(regid) <> 11:
		return 'invalid reg_id'

	_jpush = jpush.JPush(settings.JPUSH_APP_KEY, settings.JPUSH_APP_MASTER)

	push = _jpush.create_push()
	push.audience = jpush.registration_id(regid)
	push.notification = jpush.notification(ios=jpush.ios(alert='', content_available=True, extras={"like_num": like_num, "action": "like"}))
	push.options = dict(apns_production=False)

	push.platform = jpush.platform('ios')
	return push.send()

def _weibo(access_token, expire):
	client = APIClient(app_key=settings.SINA_APP_KEY, app_secret=settings.SINA_APP_SECRET, redirect_uri=settings.SINA_CALLBACK_URL)
	client.set_access_token(access_token, expire)
	return client

def sina_get_user_info(access_token, expire, uid):
	client = _weibo(access_token, expire)
	wb = client.get.users__show(uid=uid)

	return wb

def sina_follow(access_token, expire, uid):
	client = _weibo(access_token, expire)
	try:
		wb = client.post.friendships__create(uid=uid)
	except:
		return None

	return wb

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


def calculate_age(born):
    today = date.today()
    try: 
        birthday = born.replace(year=today.year)
    except ValueError: # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year, day=born.day-1)
	print birthday, today
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year

def index(request):
	from django.shortcuts import render_to_response
	return render_to_response('index.html')


