# -*- coding:utf-8 -*-
from util.daemonextension import DaemonCommand
from django.db import models
#from placeholders import *
import datetime
import time
import os

from apns import APNs, Payload
from util.models import APNS
from util.views import send_msg_apns
from django.db import transaction
from django.conf import settings
    
class Command(DaemonCommand):
	def push_apns(self):
		from people.models import Profile
		while True:
			push_apns = APNS.objects.filter(publish_date__lt=datetime.datetime.now(), is_pushed=False)

			if push_apns.count() > 0:
				print u'%s: %i ready.' % (datetime.datetime.now(), push_apns.count())
				apns_send = APNs(use_sandbox=True, cert_file=settings.CERT_PEM, key_file=settings.KEY_PEM)

				profiles = Profile.objects.filter(deviceid__isnull=False).exclude(deviceid='').exclude(deviceid='faketoken').values('deviceid').distinct()
				for apns in push_apns:
					print u'%s: %s to be pushed.' % (datetime.datetime.now(), apns.content)

					payload = Payload(alert=apns.content, sound="default", badge=1, custom={})

					i = 0
					for profile in profiles:
						try:
							i += 1
							if i % 50 == 0:
								apns_send = APNs(use_sandbox=True, cert_file=settings.CERT_PEM, key_file=settings.KEY_PEM)
							apns_send.gateway_server.send_notification(profile['deviceid'], payload)
							print u'%s: %s complete.' % (datetime.datetime.now(), profile['deviceid'])
						except:
							raise
							print u'%s: %s error.' % (datetime.datetime.now(), profile['deviceid'])

					print u'%s: %s completed' % (datetime.datetime.now(), apns.content)
					apns.is_pushed = True
					apns.save()
			else:
				print u'%s: no task. sleep....' % datetime.datetime.now()
				
				
			time.sleep(60)

	def handle(self, *args, **options):
		self.push_apns()

	#def handle_daemon(self, *args, **options):
	#	self.push_apns()


