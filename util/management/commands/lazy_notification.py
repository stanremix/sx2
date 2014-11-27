# -*- coding:utf-8 -*-
from util.daemonextension import DaemonCommand
from django.db import models
#from placeholders import *
import datetime
import time
import os

from apns import APNs, Payload
from util.models import APNS
from django.conf import settings
from util.views import send_single_apns
from django.db import transaction
    
class Command(DaemonCommand):
	def lazy_notification(self):
		from people.models import Profile
		import random
		while True:
			transaction.enter_transaction_management()
			targets = Profile.objects.filter(login_time__lt=datetime.datetime.now()-datetime.timedelta(hours=36), is_valid=True)

			if targets.count() > 0:
				rd = random.randrange(3,10)
				for target in targets:
					if target.gender == 0:
						send_single_apns(target.deviceid, u'请再多爱我一天，因为%d位帅哥正单身~~赶紧去看看吧！' % rd, badge=1)
					else:
						send_single_apns(target.deviceid, u'请再多爱我一天，因为%d位美女正单身~~赶紧去看看吧！' % rd, badge=1)


			transaction.commit()
			time.sleep(86400)

	#def handle(self, *args, **options):
	#	self.lazy_notification()

	def handle_daemon(self, *args, **options):
		self.lazy_notification()

	#def handle_daemon(self, *args, **options):
	#	self.clear_couple()


