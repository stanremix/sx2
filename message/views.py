# Create your views here.

from django.http import HttpResponse
from util import HttpAjaxResponse
from message.models import Message, MessageToUser
from people.models import Profile, Relation
from django.contrib.auth.models import User
from django.conf import settings
from upyun.util import upload_pic
from util.views import send_new_photo_notification, send_like_notification
import datetime
import time
import random

def view_message(request):
	uid = request.GET.get('user_id',0)
	tid = request.GET.get('to_user_id',0)

	fuser = User.objects.get(id=uid)
	tuser = User.objects.get(id=tid)

	msgs = MessageToUser.objects.filter(user=fuser, message__user=tuser, status=0).update(status=2, read_date=datetime.datetime.now())

	res = []
		
	rels = Relation.objects.filter(fuser=fuser, tuser=tuser, is_like=True)

	if rels.count() > 0:
		rel = rels[0]
		rel.new = 0
		rel.update_time = None
		rel.save()

	return HttpAjaxResponse(content=dict(data=res))


def send(request):
	if request.POST:
		uid = request.POST.get('user_id',0)
		tid = request.POST.get('to_user_id',0)
		typ = request.POST.get('type')
		txt = request.POST.get('txt')
		lon = request.POST.get('lon')
		lat = request.POST.get('lat')
		cityname = request.POST.get('city')

		time_stamp = time.mktime(datetime.datetime.now().timetuple())
		url = ''

		to_user_array = tid.split(',')
		user = User.objects.get(id=uid)
		photo_id = '%s_%d' % (uid, time_stamp)

		if request.FILES.get('photo'):
			url = '%s%s' % (settings.UPYUN_AVATAR_PREFIX, photo_id)
			upload_pic(request.FILES.get('photo'), photo_id)

		lon = 0 if not lon else float(lon)
		lat = 0 if not lat else float(lat)

		msg = Message.objects.create(user=user, photo=url, txt=txt, lon=lon, lat=lat, city=cityname)
		user.get_profile().photo = msg
		user.get_profile().save()

		toids = []

		admin_reply = False

		if to_user_array[0] == '0':
			rels = Relation.objects.filter(tuser=user, is_like=True).select_related()

			for rel in rels:
				if rel.is_mutal and not ('%i' % rel.fuser.id in to_user_array):
					continue

				rel.new += 1
				rel.update_time = datetime.datetime.now()
				rel.save()
				to_msg = MessageToUser.objects.create(message=msg, user=rel.fuser, is_mutal=rel.is_mutal)
			
				if rel.fuser.get_profile().reg_id and len(rel.fuser.get_profile().reg_id) == 11:
					toids.append(rel.fuser.get_profile().reg_id)

		else:
			to_user_array.remove('')
			usrs = User.objects.filter(id__in=to_user_array)

			rels = Relation.objects.filter(tuser=user, is_like=True, is_mutal=True).values('fuser')

			mutal_f = [rel['fuser'] for rel in rels]

			for usr in usrs:
				to_msg = MessageToUser.objects.create(message=msg, user=usr, is_mutal = True if usr.id in mutal_f else False)

				if usr.id == settings.ADMIN_ID:
					admin_reply = True

				if usr.get_profile().reg_id and len(usr.get_profile().reg_id) == 11:
					toids.append(usr.get_profile().reg_id)

		if len(toids) > 0:
			print msg.apns_json()
			send_new_photo_notification(tuple(toids), msg.apns_json())

		if admin_reply:
			return HttpAjaxResponse(content=dict(data=get_admin_reply()))
		else:
			return HttpAjaxResponse(content=dict(data=msg.json()))
	else:
		return HttpResponse(''' 
				<form action='' method='post' enctype='multipart/form-data'>
				id: <input type='text' name='user_id'>
				tuser: <input type='text' name='to_user_id'>
				type: <input type='text' name='type'>
				txt: <input type='text' name='txt'>
				lon: <input type='text' name='lon'>
				lat: <input type='text' name='lat'>
				city: <input type='text' name='city'>
				photo: <input type='file' name='photo'>
				<input type='submit'>
				</form>''')

def get_admin_reply():
	adm_msg = Message.objects.filter(user__id=settings.ADMIN_ID, typ='a', is_valid=True)

	return random.choice(adm_msg).json() if adm_msg.count() > 0 else None

def like(request):
	if request.POST:
		uid = request.POST.get('user_id',0)
		mid = request.POST.get('message',0)

		meses = MessageToUser.objects.filter(message__id=mid, user__id=uid).select_related()

		mes = meses[0] if meses.count() > 0 else None

		#if mes and mes.status <> 1:
		if mes:
			mes.status = 1
			mes.save()

			prf = mes.message.user.get_profile()
			prf.like_num += 1
			prf.save()

			send_like_notification(prf.reg_id, prf.like_num)

			return HttpAjaxResponse(content=dict(data='ok'))
		else:
			return HttpAjaxResponse(content=dict(data='nok'))

	else:
		return HttpResponse(''' 
				<form action='' method='post' enctype='multipart/form-data'>
				id: <input type='text' name='user_id'>
				mid: <input type='text' name='message'>
				<input type='submit'>
				</form>''')

	

	

