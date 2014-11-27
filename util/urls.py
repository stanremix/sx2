# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = patterns('util.views',
	url(r'^apns/$', 'apns'),
	url(r'^mapns/$', 'mapns'),
)
