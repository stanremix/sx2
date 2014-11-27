# -*- coding:utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from util.models import DefaultModel
import datetime

# Create your models here.
class Message(DefaultModel):
	user = models.ForeignKey(User)
	photo = models.CharField(max_length=300, null=True, blank=True)
	txt = models.CharField(max_length=300, null=True, blank=True)
	typ = models.CharField(max_length=30, null=True, blank=True)
	lon = models.FloatField(null=True, blank=True)
	lat = models.FloatField(null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		verbose_name = 'Message Log'
		verbose_name_plural = 'Message Log'

	def __unicode__(self):
		return u'%s - %s' % (self.user.get_profile().name, self.photo)

	def json(self):
		json = dict()
		json = self.user.get_profile().short_json()

		photo = dict()
		photo['id'] = self.id
		photo['photo'] = self.photo

		json['photo'] = [photo]
		json['is_mutal'] = False

		return json

	def apns_json(self):
		json = dict()
		json['i'] = self.user.id
		json['n'] = self.user.get_profile().name
		json['a'] = self.user.get_profile().avatar[len(settings.UPYUN_AVATAR_PREFIX):]

		photo = dict()
		photo['i'] = self.id
		photo['p'] = self.photo[len(settings.UPYUN_AVATAR_PREFIX):]

		json['p'] = [photo]

		return json


class MTUManager(models.Manager):
	def entry(self, user):
		result = []
		msgs = self.filter(user=user, status=0).order_by('-create_time')

		for msg in msgs:
			is_added = False
			for res in result:
				if res['user_id'] == msg.message.user.id:
					new_photo = dict()
					new_photo['id'] = msg.message.id
					new_photo['photo'] = msg.message.photo
					res['photo'].append(new_photo)
					is_added = True

					break
			if not is_added:
				result.append(msg.json())

		return result

	def total_like(self, user):
		like_num = self.filter(message__user=user, status=1).count()

		return like_num

class MessageToUser(DefaultModel):
	GENDER_CHOICES=(
		(0, u'未读'),
		(1, u'赞'),
		(2, u'pass'),
	)
	message = models.ForeignKey(Message)
	user = models.ForeignKey(User)
	status = models.IntegerField(default=0)
	is_mutal = models.BooleanField(default=False)
	read_date = models.DateTimeField(null=True, blank=True)

	objects = MTUManager()

	class Meta:
		verbose_name = 'Message Sent Log'
		verbose_name_plural = 'Message Sent Log'

	def __unicode__(self):
		return u'%s - %s' % (self.message.user.get_profile().name, self.user.get_profile().name)

	def json(self):
		json = dict()
		json = self.message.user.get_profile().short_json()

		photo = dict()
		photo['id'] = self.message.id
		photo['photo'] = self.message.photo

		json['photo'] = [photo]
		json['is_mutal'] = self.is_mutal

		return json




