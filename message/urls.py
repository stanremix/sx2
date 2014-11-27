# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = patterns('message.views',
	url(r'^like/$', 'like'),
	url(r'^send/$', 'send'),
	url(r'^view/$', 'view_message'),
)
