# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = patterns('people.views',
	url(r'^device/$', 'device'),
	url(r'^register/$', 'new_user'),
	url(r'^discover/$', 'discover'),
	url(r'^add_friend/$', 'add_friend'),
	url(r'^follow_list/$', 'follow_list'),
	url(r'^feedback/$', 'feedback'),
	url(r'^update_profile/$', 'update_profile'),

	url(r'^sina_login/$', 'sina_login'),
	url(r'^sayhi/$', 'sayhi'),
	url(r'^check_update/$', 'check_update'),
	url(r'^message/$', 'message'),
	url(r'^respond/$', 'respond'),
	url(r'^resend/$', 'resend'),
	url(r'^change_push/$', 'change_push'),
	url(r'^match_couple/$', 'adv_match_couple'),
	url(r'^adv_match_couple/$', 'adv_match_couple'),
	url(r'^couplelog/$', 'couplelog'),
	url(r'^couplemsg/$', 'couplemsg'),
	url(r'^decouple/$', 'decouple'),
	url(r'^location/$', 'location'),

	url(r'^delphoto/$', 'delphoto'),
	url(r'^get_feedback/$', 'get_feedback'),
	url(r'^get_sys_feedback/$', 'get_sys_feedback'),
	url(r'^admin_feedback/$', 'admin_feedback'),
	url(r'^gps/$', 'gps'),
	url(r'^entry/$', 'entry'),
	url(r'^extend/$', 'extend'),
	url(r'^avatar_list/$', 'avatar_list'),
	url(r'^verify_avatar/$', 'verify_avatar'),
	url(r'^set_condition/$', 'set_condition'),
	url(r'^bonus_num/$', 'bonus_num'),
	url(r'^rating_couple/$', 'rating_couple'),
)
