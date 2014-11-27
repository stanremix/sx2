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
from util.views import send_couple_apns
from django.db import transaction
    
class Command(DaemonCommand):
	def clear_couple(self):
		from people.models import Couple, CoupleLog
		while True:
			transaction.enter_transaction_management()
			couples = Couple.objects.filter(end_time__lt=datetime.datetime.now(), is_valid=True)

			if couples.count() > 0:
				for couple in couples:
					couple.is_valid = False
					couple.save()

					try:
						couple.fuser.get_profile().couple = None
						couple.fuser.get_profile().save()
						send_couple_apns(couple.fuser, settings.LOG_COUPLE_EXPIRED_TXT, 'rm')
					except:
						print 'fuser error'

					try:
						couple.tuser.get_profile().couple = None
						couple.tuser.get_profile().save()
						send_couple_apns(couple.tuser, settings.LOG_COUPLE_EXPIRED_TXT, 'rm')
					except:
						print 'tuser error'

					coupleLog = CoupleLog(couple=couple, user=couple.fuser, content=settings.LOG_COUPLE_DISMATCH_TXT)
					coupleLog.save()

					print couple.id, ' expired and decoupled'

			transaction.commit()
			time.sleep(60)

	def handle(self, *args, **options):
		self.clear_couple()

	#def handle_daemon(self, *args, **options):
	#	self.clear_couple()


