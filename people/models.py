# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from util.models import DefaultModel
from util.views import get_zodiac, calculate_age
from message.models import Message, MessageToUser
import datetime
import time
import random

# Create your models here.

class Relation(DefaultModel):
	fuser = models.ForeignKey(User, related_name='fuser')
	tuser = models.ForeignKey(User, related_name='tuser')
	is_like = models.BooleanField(default=False)
	is_mutal = models.BooleanField(default=False)
	is_view = models.BooleanField(default=False)
	new = models.IntegerField(default=0)
	update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

	def json(self):
		json = dict()

		json['user_id'] = self.tuser.id
		json['nickname'] = self.tuser.get_profile().name
		json['avatar'] = self.tuser.get_profile().avatar
		json['new'] = self.new
		json['is_mutal'] = self.is_mutal
		if self.update_time:
			json['update_time'] = self.update_time.strftime(settings.TIME_FORMAT)
		else:
			json['update_time'] = ''

		return json

	class Meta:
		verbose_name=u'Relation'
		verbose_name_plural=u'Relation'
		

class Profile(DefaultModel):
	GENDER_CHOICES=(
		(0, u'女生'),
		(1, u'男生'),
	)
	PROFILE_CATEGORY=(
		(0, u'待审核'),
		(1, u'普通头像'),
		(2, u'真人头像'),
		(9, u'封禁'),
	)
	user = models.OneToOneField(User, verbose_name=u'关联用户')

	name = models.CharField(max_length=50, null=True, blank=True)
	gender = models.PositiveIntegerField(verbose_name=u'性别', choices=GENDER_CHOICES, null=True, blank=True)
	avatar = models.CharField(max_length=200, null=True, blank=True)
	#last_photo = models.CharField(max_length=200, null=True, blank=True)
	cover_photo = models.CharField(max_length=200, null=True, blank=True)
	desc = models.CharField(max_length=200, null=True, blank=True)
	birthday = models.DateTimeField(null=True, blank=True)
	age = models.IntegerField(default=18, null=True, blank=True)
	zodiac = models.CharField(max_length=200, null=True, blank=True)
	wx = models.CharField(max_length=200, null=True, blank=True)
	like_num = models.IntegerField(default=0, null=True, blank=True)

	photo = models.ForeignKey(Message, null=True, blank=True)

	deviceid = models.CharField(verbose_name=u'deviceid', max_length=200)
	reg_id = models.CharField(verbose_name=u'regid', max_length=200, null=True, blank=True)
	push_setting = models.CharField(verbose_name=u'push_setting', max_length=20, null=True, blank=True, default='1')
	login_time = models.DateTimeField(null=True, blank=True, auto_now_add=True)
	is_guest = models.BooleanField(default=True)

	profile_category = models.PositiveIntegerField(verbose_name=u'用户分类', choices=PROFILE_CATEGORY, null=True, blank=True, default=0)

	def __unicode__(self):
		return u'%i - %s:%s' % (self.user.id, self.name, self.avatar)

	class Meta:
		verbose_name=u'Profile'
		verbose_name_plural=u'Profile'

	def short_info(self):
		return '%s | %d %s' % (self.get_gender_display(), self.age, self.zodiac)

	def apns_json(self):
		json = dict()
		json['i'] = self.user.id
		json['n'] = self.name or ''
		json['a'] = self.avatar[len(settings.UPYUN_AVATAR_PREFIX):]
		json['m'] = True
		
		return json

	def short_json(self, mutal=False):
		json = dict()
		json['user_id'] = self.user.id
		json['nickname'] = self.name or ''
		json['avatar'] = self.avatar or ''

		if mutal:
			json['is_mutal'] = True

		return json

	def discover_json(self, tuser):
		json = dict()
		json['user_id'] = self.user.id
		json['nickname'] = self.name or ''
		json['gender'] = self.gender or 0
		json['avatar'] = self.avatar or ''
		if not self.cover_photo or self.cover_photo == '':
			json['cover'] = json['avatar']
		else:	
			json['cover'] = self.cover_photo

		json['time'] = self.login_time.strftime(settings.TIME_FORMAT)

		rel = Relation.objects.filter(fuser=self.user, tuser=tuser, is_like=True)

		#if rel.count() > 0:
		#	json['is_mutal'] = True
		#else:
		#	json['is_mutal'] = False

		json['is_mutal'] = True if rel.count() > 0 else False
		return json
	
	def mutal(self):
		rels = Relation.objects.filter(fuser=self.user, is_mutal=True)

		return [rel.tuser.get_profile().short_json(mutal=True) for rel in rels]

	def follow_num(self):
		rels = Relation.objects.filter(fuser=self.user, is_like=True)

		return rels.count()

	def json(self, isSelf=False, isCouple=False):
		json = dict()
		json['user_id'] = self.user.id
		json['nickname'] = self.name or ''
		json['gender'] = self.gender or 0
		json['avatar'] = self.avatar or ''
		json['avatar_mid'] = '%s!mid' % json['avatar']
		json['desc'] = self.desc or ''
		json['profile_category'] = self.profile_category or 0
		json['login_time'] = self.login_time.strftime(settings.TIME_FORMAT)
		json['is_guest'] = self.is_guest
		#json['like_num'] = MessageToUser.objects.total_like(self.user)
		json['like_num'] = self.like_num

		if self.birthday:
			json['birthday'] = self.birthday.strftime(settings.DATE_FORMAT)
			age = calculate_age(self.birthday.date())

			json['age'] = u'%d 岁' % int(age)
			json['zodiac'] = get_zodiac(self.birthday)
		else:
			age = 18
			json['birthday'] = '2000-01-01'
			json['age'] = '--'
			json['zodiac'] = '--'

		json['fan_num'] = Relation.objects.filter(tuser=self.user, is_like=True).count()
		json['wx'] = self.wx or ''
		json['push_setting'] = self.push_setting or ''

		if self.gender == 0:
			gender_txt = u'女生'
		else:
			gender_txt = u'男生'

		json['gender_txt'] = gender_txt
		json['full_short_info'] = u'%s %d岁 %s' % (gender_txt, age, self.zodiac or '')

		return json

class AuthManager(models.Manager):
	def validate_auth(self, wb_id, auth_from):
		user_auth = self.filter(auth_id=wb_id, auth_from=auth_from)

		if user_auth.count() > 0:
			return user_auth[0].user.get_profile(), user_auth[0]

		return None, None

class Auth(DefaultModel):
	user = models.ForeignKey(User)
	auth_id = models.CharField(verbose_name=u'auth_id', max_length=100)
	auth_from = models.CharField(verbose_name=u'auth_from', max_length=100, default='sina')
	access_token = models.CharField(verbose_name=u'access_token', max_length=100)
	expire = models.CharField(verbose_name=u'expire', max_length=100, blank=True)

	objects = AuthManager()

	class Meta:
		verbose_name=u'Auth'
		verbose_name_plural=u'Auth'

class FeedbackManager(models.Manager):
	def unread(self, user):
		lasttime = user.get_profile().feedback_time
		messages = self.filter(user=user, is_system=True)
		if lasttime:
			messages = messages.filter(create_time__gt=lasttime)

		return messages.count()

	def user(self, uid, offset, limit):
		fbs = self.filter(user__id=uid).order_by('-create_time')

		result = []
		for fb in fbs[offset:limit+offset]:
			result.append(fb.json())
		
		return result

	def sys(self, offset, limit):
		fbs = self.filter(is_system=False).order_by('-create_time')

		result = []
		for fb in fbs[offset:limit+offset]:
			result.append(fb.json())
		
		return result

class Feedback(DefaultModel):
	CATEGORY_CHOICES=(
		(0, u'反馈意见'),
		(1, u'用户举报'),
	)
	user = models.ForeignKey(User)
	feedback = models.CharField(max_length=1000)
	level = models.IntegerField(default=0, choices=CATEGORY_CHOICES)
	status = models.IntegerField(default=0)
	reply_text = models.CharField(max_length=200, null=True, blank=True)
	update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	is_system = models.BooleanField(default=False)

	objects = FeedbackManager()

	def json(self):
		json = dict()
		json['id'] = self.id
		json['is_system'] = self.is_system

		if self.is_system:
			json['avatar'] = 'http://ava19.b0.upaiyun.com/111111_111111.jpg'
			json['category'] = u'客服回复'
		else:
			json['avatar'] = self.user.get_profile().avatar
			json['category'] = self.get_level_display()

		json['user_id'] = self.user.id
		json['text'] = self.feedback
		json['create_time'] = self.create_time.strftime(settings.TIME_FORMAT)

		return json

	class Meta:
		verbose_name=u'Feedback'
		verbose_name_plural=u'Feedback'

	def __unicode__(self):
		return u'%i - %i: %s' % (self.user.id, self.level, self.feedback)

class UserLogManager(models.Manager):
	def user_last_log(self, uid):
		recs = self.filter(user__id=uid).order_by('-create_time')

		if recs.count() > 0:
			return recs[0].json()
		else:
			return None

class User_Log(DefaultModel):
	ACTION_CHOICES=(
		(0, u'Register'),
		(1, u'Login'),
		(2, u'GPS Location'),
	)

	user = models.ForeignKey(User)
	lon = models.FloatField(null=True, blank=True)
	lat = models.FloatField(null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	action = models.IntegerField(default=1)

	objects = UserLogManager()

	def json(self):
		json = dict()
		json['id'] = self.id
		json['user_id'] = self.user.id
		json['lon'] = self.lon or 0
		json['lat'] = self.lat or 0
		json['city'] = self.city or ''
		
		return json

	class Meta:
		verbose_name=u'User Login Log'
		verbose_name_plural=u'User Login Log'

