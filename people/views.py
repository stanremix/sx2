# -*- coding:utf-8 -*-
# Create your views here.

from util import HttpAjaxResponse
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q

#from people.models import Auth, Profile, Message, Feedback, User_Log, Couple, CoupleLog, Photo, ActRule, User_GPS, RoleRelationship
from people.models import Auth, Profile, User_Log, Relation, Feedback
from message.models import Message, MessageToUser
from util.views import sina_get_user_info, sina_follow, calculate_age, send_friend_notification
from upyun.util import upload_pic

import datetime
from datetime import timedelta
import time
import random

def device(request):
	if request.POST:
		uid = request.POST.get('user_id')
		dtoken = request.POST.get('deviceid')
		rid = request.POST.get('reg_id')

		user = User.objects.get(id=uid)

		user.get_profile().deviceid = dtoken
		user.get_profile().reg_id = rid

		user.get_profile().save()

		return HttpAjaxResponse(content=dict(data='ok'))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			userid: <input type='text' name='user_id'>
			dtoken: <input type='text' name='deviceid'>
			regid: <input type='text' name='reg_id'>
			<input type='submit'>
			</form>''')

def follow_list(request):
	uid = request.GET.get('user_id')

	follow_list = Relation.objects.filter(fuser__id=uid, is_like=True)

	result = [fol.json() for fol in follow_list[:30]]

	return HttpAjaxResponse(content=dict(data=result))

def discover(request):
	uid = request.GET.get('user_id')
	keyword = request.GET.get('keyword')
	page = int(request.GET.get('page', 0))
	size = 20

	user = User.objects.get(id=uid)

	if keyword:
		tobe_friend = Profile.objects.filter(is_guest=False, name__contains=keyword)[page*size:(page+1)*size]
	else:
		existed_rel = Relation.objects.filter(fuser=user).values('tuser')
		existed_array = []

		for rel in existed_rel:
			existed_array.append(rel['tuser'])

		existed_array.append(user.id)

		tobe_friend = Profile.objects.filter(is_guest=False).exclude(user__in=existed_array)

	# random result set
	tobe_friend = random.sample(tobe_friend, 20) if tobe_friend.count() >= 20 else tobe_friend

	# record view history
	for tf in tobe_friend:
		res = Relation.objects.get_or_create(fuser=user, tuser=tf.user)

	# turn into json format
	result_friend = [tobe.discover_json(user) for tobe in tobe_friend]

	return HttpAjaxResponse(content=dict(data=result_friend))

def add_friend(request):
	if request.POST:
		fuserid = request.POST.get('user_id', 0)
		tuserid = request.POST.get('to_user_id', 0)
		is_like = request.POST.get('is_like', 1)

		fuser = User.objects.get(id=fuserid)
		tuser = User.objects.get(id=tuserid)

		result = dict()

		res, is_created = Relation.objects.get_or_create(fuser=fuser, tuser=tuser)

		is_like = True if is_like == '1' else False

		res.is_like = is_like

		if is_like:
			reverse_rels = Relation.objects.filter(fuser=tuser, tuser=fuser, is_like=True)

			if reverse_rels.count() > 0:
				rev_rel = reverse_rels[0]
				rev_rel.is_mutal = True
				res.is_mutal = True
				rev_rel.save()

				#inform
				if tuser.get_profile().reg_id and len(tuser.get_profile().reg_id) == 11:
					send_friend_notification(tuser.get_profile().reg_id, fuser.get_profile().apns_json())

			if not res.is_view and tuser.get_profile().photo:
				to_msg = MessageToUser.objects.create(message=tuser.get_profile().photo, user=fuser, is_mutal = res.is_mutal)
				result['photo'] = to_msg.json()

		res.is_view = True
		res.save()

		result['user'] = res.json()
		result['is_like'] = is_like

		return HttpAjaxResponse(content=dict(data=result))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			fuserid: <input type='text' name='user_id'>
			tuserid: <input type='text' name='to_user_id'>
			is_like: <input type='text' name='is_like'>
			<input type='submit'>
			</form>''')

def feedback(request):
	if request.POST:
		uid = int(request.POST.get('user_id',0))
		fbtxt = request.POST.get('feedback')
		category = request.POST.get('category')
		
		if not category:
			category = 0
		else:
			category = int(category)

		user = User.objects.get(id=uid)
		fb = Feedback(user=user, feedback=fbtxt, level=category)
		fb.save()

		return HttpAjaxResponse(content=dict(data=dict(status=100)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='user_id'>
			feedback: <input type='text' name='feedback'>
			category: <input type='text' name='category'>
			<input type='submit'>
			</form>''')


def entry(request):
	uid = int(request.GET.get('user_id', 0))
	lon = request.GET.get('lon')
	lat = request.GET.get('lat')
	cityname = request.GET.get('city')

	if lon and lat:
		user = User.objects.get(id=uid)
		User_Log.objects.create(user=user, lon=lon, lat=lat, city=cityname, action=1)

	user_dict = pack_entry_data_of_user(uid)

	return HttpAjaxResponse(content=dict(data=user_dict))

def pack_entry_data_of_user(uid):
	user = User.objects.get(id=uid)

	unread = MessageToUser.objects.entry(user=user)

	user_dict = user.get_profile().json()
	user_dict['fan'] = user.get_profile().mutal()
	user_dict['follow_num'] = user.get_profile().follow_num()

	return dict(version=1, user=user_dict, unread=unread)

def update_profile(request):
	if request.POST:
		uid = request.POST.get('user_id')

		nickname = request.POST.get('nickname')
		gender = request.POST.get('gender')
		lon = request.POST.get('lon')
		lat = request.POST.get('lat')
		cityname = request.POST.get('city')

		user = User.objects.get(id=uid)

		if lon and lat:
			User_Log.objects.create(user=user, lon=lon, lat=lat, city=cityname, action=1)
		
		time_stamp = time.mktime(datetime.datetime.now().timetuple())
		avatar = '%s_%d' % (uid, time_stamp)

		usr_profile = user.get_profile()

		usr_profile.name = nickname
		#usr_profile.birthday = birthday
		if gender:
			usr_profile.gender = gender

		#usr_profile.age = calculate_age(usr_profile.birthday.date())
		usr_profile.is_guest = False

		if request.FILES.get('avatar'):
			usr_profile.avatar = '%s%s' % (settings.UPYUN_AVATAR_PREFIX, avatar)
			usr_profile.profile_category = 0
			usr_profile.update_time = datetime.datetime.now()
			upload_pic(request.FILES.get('avatar'), avatar)

		usr_profile.save()

		return HttpAjaxResponse(content=dict(data=usr_profile.json()))
	else:
		return HttpResponse(''' 
			<form action='' method='post' enctype='multipart/form-data'>
			id: <input type='text' name='user_id'>
			nickname: <input type='text' name='nickname'>
			gender: <input type='text' name='gender'>
			birthday: <input type='text' name='birthday'>
			avatar: <input type='file' name='avatar'>
			<input type='submit'>
			</form>''')
		
	return HttpAjaxResponse(content=dict(data='hehe'))

def new_user(request):
	if request.POST:
		lon = request.POST.get('lon')
		lat = request.POST.get('lat')
		cityname = request.POST.get('city')
		deviceid = request.POST.get('deviceid')

		time_stamp = time.mktime(datetime.datetime.now().timetuple())

		uname = '%s_%i' % (deviceid[0:8], time_stamp)
		usr = User(username=uname)
		usr.save()
		usr_profile = Profile(user=usr)
		usr_profile.deviceid = deviceid
		usr_profile.is_guest = True
		usr_profile.save()

		if lon and lat:
			User_Log.objects.create(user=usr, lon=lon, lat=lat, city=cityname, action=0)

		# add sys user
		sys_user = User.objects.get(id=settings.ADMIN_ID)

		rel1 = Relation.objects.create(fuser=usr, tuser=sys_user, is_like=True, is_mutal=True, is_view=True)
		rel2 = Relation.objects.create(fuser=sys_user, tuser=usr, is_like=True, is_mutal=True, is_view=True)

		user_dict = pack_entry_data_of_user(usr.id)

		return HttpAjaxResponse(content=dict(data=user_dict))
	else:
		return HttpResponse(''' 
			<form action='' method='post' enctype='multipart/form-data'>
			deviceid: <input type='text' name='deviceid'>
			<input type='submit'>
			</form>''')

def location(request):
	uid = int(request.GET.get('uid', 0))
	tid = int(request.GET.get('tid', 0))

	#json = User_Log.objects.user_last_log(tid)
	try:
		ugps = User_GPS.objects.get(user__id=tid)
		return HttpAjaxResponse(content=dict(data=ugps.json()))
	except:
		return HttpAjaxResponse(content=dict(data=None))


def gps(request):
	if request.POST:
		uid = request.POST.get('uid',0)
		lon = request.POST.get('lon')
		lat = request.POST.get('lat')
		city = request.POST.get('city')
		gender = request.POST.get('gender')

		user = User.objects.get(id=uid)

		gps, is_created = User_GPS.objects.get_or_create(user=user)
		gps.lon = float(lon)
		gps.lat = float(lat)
		gps.city = city
		gps.gender = gender
		gps.update_time = datetime.datetime.now()
		gps.save()

		user.get_profile().city_code = city
		user.get_profile().save()
		return HttpAjaxResponse(content=dict(data=gps.json()))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			lon: <input type='text' name='lon'>
			lat: <input type='text' name='lat'>
			city: <input type='text' name='city'>
			<input type='submit'>
			</form>''')

@transaction.commit_on_success
def old_register(request):
	if request.POST:
		deviceid = request.POST.get('deviceid')
		time_stamp = time.mktime(datetime.datetime.now().timetuple())

		uname = '%s_%i' % (deviceid[0:8], time_stamp)
		usr = User(username=uname)
		usr.save()
		usr_profile = Profile(user=usr)
		usr_profile.deviceid = deviceid
		usr_profile.is_guest = True
		usr_profile.save()
		
		return HttpAjaxResponse(content=dict(data=usr_profile.json()))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			deviceid: <input type='text' name='deviceid'>
			<input type='submit'>
			</form>''')


@transaction.commit_on_success
def sina_login(request):
	if request.POST:
		wb_id = request.POST.get('id')
		access_token = request.POST.get('access_token')
		expire = request.POST.get('expire')
		deviceid = request.POST.get('deviceid')
		lon = request.POST.get('lon')
		lat = request.POST.get('lat')
		city = request.POST.get('city')

		user, usr_auth = Auth.objects.validate_auth(wb_id, 'sina')

		if not user:
			user_wb_info = sina_get_user_info(access_token, expire, wb_id)
			usr = User(username= 'wb_%s' % wb_id)
			usr.save()
			usr_profile = Profile(user=usr)
			usr_profile.name = user_wb_info['screen_name']
			usr_profile.avatar = user_wb_info['avatar_large']
			usr_profile.desc = user_wb_info['description']
			usr_profile.deviceid = deviceid
			usr_profile.is_guest = False
			usr_profile.city = city
			birthday = datetime.datetime.strptime('1990-01-01', settings.DATE_FORMAT)
			usr_profile.birthday = birthday

			try:
				is_follow = sina_follow(access_token, expire, settings.WEIBO_ACCOUNT)
			except:
				print '!!!!!!! failed to follow'

			if user_wb_info['gender'] == 'f':
				usr_profile.gender = 0
				usr_profile.propose_num = 3
			else:
				usr_profile.gender = 1
				usr_profile.propose_num = 1

			usr_profile.save()

			usr_auth = Auth(user=usr)
			usr_auth.auth_id = wb_id
			usr_auth.auth_from = 'sina'
			usr_auth.access_token = access_token
			usr_auth.expire = expire

			usr_auth.save()

			transaction.commit()
			return HttpAjaxResponse(content=dict(data=usr_profile.json(), status=0))
		else:
			usr_auth.auth_id = wb_id
			usr_auth.auth_from = 'sina'
			usr_auth.access_token = access_token
			usr_auth.expire = expire
			usr_auth.save()

			user.deviceid = deviceid
			user.is_guest = False
			user.save()

			transaction.commit()
			return HttpAjaxResponse(content=dict(data=user.json(), status=1))
	
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			id: <input type='text' name='id'>
			at: <input type='text' name='access_token'>
			expire: <input type='text' name='expire'>
			deviceid: <input type='text' name='deviceid'>
			<input type='submit'>
			</form>''')
		
	return HttpAjaxResponse(content=dict(data='hehe'))

	
def entry_back(request):
	uid = int(request.GET.get('id', 0))
	lon = request.GET.get('lon')
	lat = request.GET.get('lat')
	cityname = request.GET.get('city')
	deviceid = request.GET.get('deviceid')

	user = User.objects.get(id=uid)
	user_profile = user.get_profile()
	user_profile.login_time = datetime.datetime.now()
	user_profile.is_valid = True
	if cityname:
		user_profile.city_code = cityname

	user_profile.save()

	User_GPS.objects.update(user=user, lon=lon, lat=lat, city=cityname)

	start_date = datetime.datetime.today().date()
	end_date = start_date + timedelta( days=1 ) 

	dt = ScheduleTable.objects.get_today_schedule()

	if dt:
		url = dt.item.url
	else:
		url = u'http://mp.weixin.qq.com/s?__biz=MjM5OTg4Mjk4MQ==&mid=200180617&idx=1&sn=94be794d2cd7bd9510a8811a53a94211#rd'

	return HttpAjaxResponse(content=dict(data=dict(version=0, user=user_profile.json(isSelf=True), notification=u'欢迎体验新的一天！^^ 麻烦广大男同胞们补全自己的个人资料，再去寻找有缘分的另一半哟！', app_daily=url, role=RoleRelationship.objects.match_role(user_profile.current_role))))

def check_update(request):
	uid = int(request.GET.get('id', 0))
	page = int(request.GET.get('page', 1))
	lon = request.GET.get('lon')
	lat = request.GET.get('lat')
	cityname = request.GET.get('city')
	deviceid = request.GET.get('deviceid')

	limit = settings.PAGE_LIMIT 
	offset = (page-1) * limit 

	city = City.objects.filter(name=cityname)

	citycode = None
	if city.count() == 0:
		citycode = cityname

	if uid == 0 and deviceid:
		user_profile = register_guest(deviceid)
		user = user_profile.user
	else:
		try:
			user = User.objects.get(id=uid)
		except:
			user = User.objects.get(id=settings.GUEST_ID)
		user_profile = user.get_profile()

	results = City.objects.get_valid_event(user, city=citycode)

	unread = User_Match_Record.objects.unread(user)

	ur = User_Log(user=user, lon=lon, lat=lat, city=cityname)
	ur.save()

	return HttpAjaxResponse(content=dict(data=dict(unread=unread, event=results, version=0, user=user_profile.json(isSelf=True))))

def change_push(request):
	if request.POST:
		uid = request.POST.get('uid')
		val = request.POST.get('val')
		push_type = int(request.POST.get('ptype'))
		usr = User.objects.get(id=uid)
		if push_type == 2:
			usr.get_profile().push_setting = val
		else:
			usr.get_profile().sys_push_setting = val

		usr.get_profile().save()

		return HttpAjaxResponse(content=dict(data=dict(status=100, push_setting=val, ptype=push_type)))

def delphoto(request):
	if request.POST:
		uid = request.POST.get('uid')
		pid = request.POST.get('pid')

		user = User.objects.get(id=uid)
		if Photo.objects.del_photo(user, pid):
			return HttpAjaxResponse(content=dict(data=dict(status=100, photo=Photo.objects.photo_of_user(user=user))))
		else:
			return HttpAjaxResponse(content=dict(data=dict(status=200)))

	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			pid: <input type='file' name='pid'>
			<input type='submit'>
			</form>''')

def sayhi(request):
	if request.POST:
		uid = request.POST.get('uid')
		mid = request.POST.get('mid')
		platform = request.POST.get('platform')

		print platform
		match_record = User_Match_Record.objects.get(id=mid)
		match_record.status=1
		match_record.update_time = datetime.datetime.now()

		match_record.save()

		from_name = match_record.user_event.nickname
		deviceid = match_record.recommend_user.get_profile().deviceid
		msg = u'小乖乖，%s 想与你交换微信呢！' % from_name
		send_valid_apns(match_record.recommend_user.get_profile(), msg, badge=1, platform=platform)
		
		return HttpAjaxResponse(content=dict(data=dict(status=100, message=match_record.json(uid))))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			mid: <input type='text' name='mid'>
			platform: <input type='text' name='platform'>
			<input type='submit'>
			</form>''')

def respond(request):
	if request.POST:
		mid = request.POST.get('mid')
		uid = request.POST.get('uid')
		result = int(request.POST.get('result'))

		message = User_Match_Record.objects.get(id=mid)
		message.status=result
		message.update_time = datetime.datetime.now()
		message.save()

		from_name = message.recommend_user.get_profile().name
		deviceid = message.user_event.user.get_profile().deviceid

		if result == 2:
			msg = u'噻，%s 把微信号告诉你了呢！赶快去看看吧！' % from_name
		elif result == 3:
			msg = u'内什么，%s 拒绝了你的请求……要不咱再试一次？' % from_name
		else:
			msg = u'%s 好像对你有点意思哟~~赶快去看看呀！' % from_name
			
		send_valid_apns(message.user_event.user.get_profile(), msg)

		return HttpAjaxResponse(content=dict(data=dict(status=100, message=message.json(int(uid)))))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			mid: <input type='text' name='id'>
			uid: <input type='text' name='uid'>
			result: <input type='text' name='result'>
			<input type='submit'>
			</form>''')

def resend(request):
	if request.POST:
		mid = request.POST.get('id')
		uid = int(request.POST.get('uid'))

		message = User_Match_Record.objects.get(id=mid)
		message.update_time = datetime.datetime.now()
		message.save()

		return HttpAjaxResponse(content=dict(data=dict(status=100, message=message.json(uid))))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			mid: <input type='text' name='id'>
			uid: <input type='text' name='uid'>
			<input type='submit'>
			</form>''')

def message(request):
	uid = request.GET.get('uid')
	page = int(request.GET.get('page', 1))
	limit = settings.PAGE_LIMIT 
	offset = (page-1) * limit 

	user = User.objects.get(id=uid)
	last_time = user.get_profile().msg_time

	if not last_time:
		last_time = datetime.datetime.strptime('1900-1-1', settings.DATE_FORMAT)
	results = []
	#messages = Message.objects.filter(Q(tuser=user)|Q(ue__user=user)).order_by('-update_time')
	messages = User_Match_Record.objects.filter(Q(recommend_user=user, status__lt=3)|Q(user_event__user=user)).filter(status__gt=0, update_time__gt=last_time).order_by('-update_time')

	for message in messages[offset:offset+limit]:
		results.append(message.json(user.id))

	if last_time:
		last_time = last_time.strftime(settings.TIME_FORMAT)
	else:
		last_time = '1900-1-1 00:00:00'

	user.get_profile().msg_time = datetime.datetime.now()
	user.get_profile().save()

	return HttpAjaxResponse(content=dict(data=dict(message=results, timestamp=last_time)))

def get_feedback(request):
	uid = int(request.GET.get('uid', 0))
	page = int(request.GET.get('page', 1))
	limit = int(request.GET.get('limit', 3))

	#limit = settings.PAGE_LIMIT 
	offset = (page-1) * limit 

	user = User.objects.get(id=uid)
	if int(page) == 1:
		user.get_profile().feedback_time = datetime.datetime.now()
		user.get_profile().save()

	return HttpAjaxResponse(content=dict(data=Feedback.objects.user(uid, offset, limit)))

def get_sys_feedback(request):
	uid = int(request.GET.get('uid', 0))
	page = int(request.GET.get('page', 1))
	limit = int(request.GET.get('limit', 3))

	offset = (page-1) * limit 

	user = User.objects.get(id=uid)

	return HttpAjaxResponse(content=dict(data=Feedback.objects.sys(offset, limit)))


def admin_feedback(request):
	if request.POST:
		uid = int(request.POST.get('uid',0))
		fbtxt = request.POST.get('feedback')
		category = request.POST.get('category')
		
		if not category:
			category = 0
		else:
			category = int(category)

		user = User.objects.get(id=uid)
		fb = Feedback(user=user, feedback=fbtxt, level=category, is_system=True)
		fb.save()

		send_msg_apns(user, u'您在一天的反馈有回复啦！请打开查看')

		return HttpAjaxResponse(content=dict(data=dict(result=fb.json(), status=100)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			feedback: <input type='text' name='feedback'>
			category: <input type='text' name='category'>
			<input type='submit'>
			</form>''')
		
def match_couple(request):
	if request.POST:
		fuid = request.POST.get('fuser',0)
		tuid = request.POST.get('tuser',0)
		city = request.POST.get('city')
		gender = request.POST.get('gender')
		
		#return HttpAjaxResponse(content=dict(data=dict(data=dict(msg='not enough user', delay=60), status=0)))
		if fuid == 0:
			return HttpAjaxResponse(content=dict(data=u'error'))

		couple_history = Couple.objects.filter(fuser__id=int(fuid), start_time__day=datetime.datetime.today().day)

		#if couple_history.count() > 0:
		#	return HttpAjaxResponse(content=dict(data=dict(data=u'今天配对机会用完，请等待明天', status=4)))
			
		couple = Couple.objects.find_couple(fuid, tuid, city, gender)

		if not couple:
			return HttpAjaxResponse(content=dict(data=dict(data=dict(msg='暂时没有合适的候选人，请稍后再试吧!', delay=60), status=0)))
		elif len(couple) > 1:
			return HttpAjaxResponse(content=dict(data=dict(data=couple, status=3)))
		else:
			return HttpAjaxResponse(content=dict(data=dict(data=couple, status=1)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			fuser: <input type='text' name='fuser'>
			tuser: <input type='text' name='tuser'>
			city: <input type='text' name='city'>
			<input type='submit'>
			</form>''')
		
def adv_match_couple(request):
	if request.POST:
		fuid = request.POST.get('fuser',0)
		tuid = request.POST.get('tuser',0)
		city = request.POST.get('city')
		gender = request.POST.get('gender')
		
		#return HttpAjaxResponse(content=dict(data=dict(data=dict(msg='not enough user', delay=60), status=0)))
		if fuid == 0:
			return HttpAjaxResponse(content=dict(data=u'error'))

		fuser = User.objects.get(id=fuid)

		# check time status:
		if not tuid or tuid == 0:
			last_search = User_Log.objects.filter(user=fuser, action=1, create_time__gt=(datetime.datetime.now()-datetime.timedelta(minutes=1))).order_by('-create_time')

			if last_search.count()>0:
				return HttpAjaxResponse(content=dict(data=dict(data=u'别着急，一分钟后才能再次搜索哟~', status=4)))
			
			ul = User_Log.objects.create(user=fuser, action=1)

		#couple_history = Couple.objects.filter(fuser__id=int(fuid), start_time__day=datetime.datetime.today().day)

		#if couple_history.count() > 0:
		#	return HttpAjaxResponse(content=dict(data=dict(data=u'今天配对机会用完，请等待明天', status=4)))
			
		couple, status = Couple.objects.adv_find_couple(fuid, tuid, city, gender)

		if not couple:
			if status == 0:
				return HttpAjaxResponse(content=dict(data=dict(data=dict(msg=u'暂时没有合适的候选人，请稍后再试吧!', delay=60), status=status)))
			else:
				return HttpAjaxResponse(content=dict(data=dict(data=dict(msg=u'啊，该用户太热门，刚刚被人选走了...'), status=status)))
		else:
			return HttpAjaxResponse(content=dict(data=dict(data=couple, status=status)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			fuser: <input type='text' name='fuser'>
			tuser: <input type='text' name='tuser'>
			city: <input type='text' name='city'>
			gender: <input type='text' name='gender'>
			<input type='submit'>
			</form>''')

def couplelog(request):
	uid = request.GET.get('uid')
	limit = int(request.GET.get('limit', 2))
	lastid = request.GET.get('lastid')

	user = User.objects.get(id=uid)
	if not user.get_profile().couple:
		return HttpAjaxResponse(content=dict(data=None))

	logs = user.get_profile().couple.log(lastid, limit)

	if not lastid or int(lastid) == 0:
		user.get_profile().msg_time = datetime.datetime.now()
		user.get_profile().save()

	return HttpAjaxResponse(content=dict(data=logs))

def couplemsg(request):
	if request.POST:
		uid = request.POST.get('uid',0)
		coupleid = request.POST.get('couple',0)
		content = request.POST.get('content')
		category = int(request.POST.get('category'))
		
		if (uid == 0) or (coupleid == 0):
			return HttpAjaxResponse(content=dict(data=u'error'))

		couple = Couple.objects.get(id=coupleid)
		user = User.objects.get(id=uid)

		if couple.fuser == user:
			tuser = couple.tuser
		else:
			tuser = couple.fuser

		if category == 4:
			msg = ActRule.objects.code(content)
			if not msg:
				msg = content
		else:
			msg = content

		time_now = datetime.datetime.strptime(datetime.datetime.now().strftime(settings.TIME_FORMAT), settings.TIME_FORMAT)
		coupleLog, is_created = CoupleLog.objects.get_or_create(couple=couple, user=user, content=msg, category=category, create_time=time_now)

		if not is_created:
			return HttpAjaxResponse(content=None)

		if request.FILES.get('data'):
			avatar = '%s_%d' % (uid, coupleLog.id)

			if category == 6:
				coupleLog.content = '%s%s' % (settings.UPYUN_VIDEO_PREFIX, avatar)
				coupleLog.duration = float(msg)
				upload_pic(request.FILES.get('data'), avatar, up_type='aud')
			else:
				coupleLog.content = '%s%s' % (settings.UPYUN_DATA_PREFIX, avatar)
				upload_pic(request.FILES.get('data'), avatar, up_type='cpp')

			coupleLog.save()

		#tuser = User.objects.get(id=118)
		if category == 4:
			send_msg_apns(tuser, msg)
		else:
			send_msg_apns(tuser, None)

		return HttpAjaxResponse(content=dict(data=coupleLog.json()))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			coupleid: <input type='text' name='couple'>
			content: <input type='text' name='content'>
			category: <input type='text' name='category'>
			<input type='submit'>
			</form>''')
		
def decouple(request):
	from charge.models import CoinLog
	if request.POST:
		uid = request.POST.get('uid',0)
		coupleid = request.POST.get('couple',0)
		
		if (uid == 0) or (coupleid == 0):
			return HttpAjaxResponse(content=dict(data=u'error'))

		user = User.objects.get(id=uid)
		res = Couple.objects.break_couple(fuid=uid, coupleid=coupleid)

		if res == 98:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'您没有足够的金币')))
		elif res == 99:
			return HttpAjaxResponse(content=dict(data=dict(status=99, message=u'您还未匹配另一半')))
		else:
			coin = CoinLog.objects.user_coin(user)
			return HttpAjaxResponse(content=dict(data=dict(status=100, coin=coin)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			couple: <input type='text' name='couple'>
			<input type='submit'>
			</form>''')

def extend(request):
	from charge.models import CoinLog
	if request.POST:
		uid = request.POST.get('uid',0)
		coupleid = request.POST.get('couple',0)
		
		if (uid == 0) or (coupleid == 0):
			return HttpAjaxResponse(content=dict(data=u'error'))

		user = User.objects.get(id=uid)
		res = Couple.objects.extend_couple(fuid=uid)

		if res == 98:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'您没有足够的金币')))
		elif res == 99:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'您还未匹配另一半')))
		else:
			coin = CoinLog.objects.user_coin(user)
			return HttpAjaxResponse(content=dict(data=dict(status=100, coin=coin, delta=86400)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			couple: <input type='text' name='couple'>
			<input type='submit'>
			</form>''')

def avatar_list(request):
	uid = request.GET.get('uid')
	page = int(request.GET.get('page', 1))
	limit = int(request.GET.get('limit', 3))
	category = request.GET.get('category')
	limit = 40
	offset = (page-1) * limit 

	results = Profile.objects.filter(profile_category=category).order_by('-create_time')
	rd_data = []

	for result in results[offset:offset+limit]:
		rd_data.append(result.json())

	return HttpAjaxResponse(content=dict(data=dict(result=rd_data, count_num=results.count())))

def verify_avatar(request):
	if request.POST:
		uid = request.POST.get('uid',0)
		category = int(request.POST.get('category', 1))
		target = request.POST.get('target')

		targets = target.split(',')

		results = Profile.objects.filter(user_id__in=targets)

		if category == 9:
			results.update(profile_category=category, is_valid=False)
		else:
			results.update(profile_category=category, is_valid=True)

		for res in results:
			if res.profile_category == 9:
				res.apns(u'您的头像或昵称未通过审核，还无法正常使用一天，请重新上传')
			elif res.profile_category == 1:
				res.apns(u'恭喜！您的头像经审核为非真人头像，欢迎继续使用一天。认证为真人头像后，可以发现其他真实头像用户哟！')
			elif res.profile_category == 2:
				res.apns(u'恭喜！！您的头像通过审核，可以使用一天的全部功能。一天欢迎您的加入！')

		return HttpAjaxResponse(content=dict(data=u'success'))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			category: <input type='text' name='category'>
			target: <input type='text' name='target'>
			<input type='submit'>
			</form>''')

def set_condition(request):
	from people.models import MatchCondition
	if request.POST:
		uid = request.POST.get('uid',0)
		city = request.POST.get('city_code')
		gender = request.POST.get('gender')
		age = request.POST.get('age')
		avatar = request.POST.get('avatar')
		silence = int(request.POST.get('silence', 0))
		intention = int(request.POST.get('intention', 0))
		mycity = int(request.POST.get('mycity', 9999))

		user = User.objects.get(id=uid)

		condition, is_created = MatchCondition.objects.get_or_create(user=user)

		condition.city=city
		condition.gender=gender
		condition.profile_category=avatar
		condition.age=age
		condition.intention=intention

		condition.save()

		user.get_profile().intention = intention
		if mycity != 9999:
			user.get_profile().city_code = mycity

		if silence > 0:
			if not user.get_profile().silence_time:
				user.get_profile().silence_time = datetime.datetime.now()+datetime.timedelta(hours=24*silence)

		if user.get_profile().silence_time:
			silence_time = user.get_profile().silence_time.strftime(settings.TIME_FORMAT)
		else:
			silence_time = ''

		user.get_profile().save()

		return HttpAjaxResponse(content=dict(data=dict(status=1, silence_time=silence_time)))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			city code: <input type='text' name='city_code'>
			gender: <input type='text' name='gender'>
			age: <input type='text' name='age'>
			avatar: <input type='text' name='avatar'>
			silence: <input type='text' name='silence'>
			<input type='submit'>
			</form>''')

def bonus_num(request):
	from charge.models import CoinLog
	if request.POST:
		uid = request.POST.get('uid',0)
		price = int(request.POST.get('price', 0))
		
		if (uid == 0) or (price == 0):
			return HttpAjaxResponse(content=dict(data=u'error'))

		user = User.objects.get(id=uid)
		res = user.get_profile().add_num(price)

		if res == 98:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'您没有足够的金币')))
		else:
			coin = CoinLog.objects.user_coin(user)
			return HttpAjaxResponse(content=dict(data=dict(status=100, message=u'恭喜！已经成功开启一个新的推荐名额!', user=user.get_profile().json(isSelf=True))))
	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			price: <input type='text' name='price'>
			<input type='submit'>
			</form>''')

def rating_couple(request):
	from people.models import CoupleRating
	from charge.models import CoinLog
	if request.POST:
		uid = request.POST.get('uid',0)
		couple = int(request.POST.get('couple',0))
		tid = int(request.POST.get('tid',0))
		category = int(request.POST.get('category',0))
		
		if (uid == 0) or (couple == 0) or (tid == 0):
			return HttpAjaxResponse(content=dict(data=u'error'))

		user = User.objects.get(id=uid)
		cp = Couple.objects.get(id=couple)
		tuser = User.objects.get(id=tid)

		coins = 0
		if category < 10:
			coins = 20
			coinlog = CoinLog.objects.create(user=user, coin=coins, tag=1)

		cr, is_created = CoupleRating.objects.get_or_create(couple=cp, user=tuser)

		if is_created:
			cr.category=category
			cr.save()
		else:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'您已经评价过啦！')))
		
		if cr:
			if category < 10:
				return HttpAjaxResponse(content=dict(data=dict(status=100, message=u'评价成功！金币增加 20 枚', coin=coins)))
			else:
				return HttpAjaxResponse(content=dict(data=dict(status=100, message=u'举报成功！', coin=coins)))
		else:
			return HttpAjaxResponse(content=dict(data=dict(status=98, message=u'出错啦，请稍后再试！')))

	else:
		return HttpResponse(''' 
			<form action='' method='post'>
			uid: <input type='text' name='uid'>
			couple: <input type='text' name='couple'>
			tid: <input type='text' name='tid'>
			category: <input type='text' name='category'>
			<input type='submit'>
			</form>''')

