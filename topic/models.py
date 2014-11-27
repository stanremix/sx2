# -*- coding:utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from util.models import DefaultModel
import datetime

# Create your models here.
class Category(DefaultModel):
	name = models.CharField(max_length=50, null=True, blank=True)
	desc = models.CharField(max_length=500, null=True, blank=True)
	update_date = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Category'

	def __unicode__(self):
		return u'%s' % self.name

class TopicManager(models.Manager):
	def _all(self):
		topics = self.all()

		res = []
		for tp in topics:
			res.append(tp.json())

		return res

class Topic(DefaultModel):
	title = models.CharField(max_length=50, null=True, blank=True)
	category = models.ForeignKey(Category, null=True, blank=True)
	bgcolor = models.IntegerField(default=0)
	desc = models.CharField(max_length=500, null=True, blank=True)
	update_date = models.DateTimeField(auto_now_add=True)

	objects = TopicManager()

	class Meta:
		verbose_name = 'Topic'
		verbose_name_plural = 'Topic'

	def __unicode__(self):
		return u'%s' % self.title

	def json(self):
		json = dict()
		json['id'] = self.id
		json['title'] = self.title
		json['category'] = self.category.name
		json['category_id'] = self.category.id
		json['bgcolor'] = self.bgcolor
		json['desc'] = self.desc
		if self.update_date:
			json['update_date'] = self.update_date.strftime(settings.TIME_FORMAT)
		else:
			json['update_date'] = ''

		return json

class UserFollowTopic(DefaultModel):
	user = models.ForeignKey(User)
	topic = models.ForeignKey(Topic)
	update_date = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name = 'User Following Topic'
		verbose_name_plural = 'User Following Topic'





