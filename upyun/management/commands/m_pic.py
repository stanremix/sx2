import uuid
import os
import time
import datetime
import urllib2
import tempfile
import Image
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.management.base import NoArgsCommand
from people.models import Profile
import cStringIO

from activity.models import Activity
from upyun.upyun import UpYun,md5,md5file
import pdb

class Command(NoArgsCommand):

	def handle_noargs(self, **options):
		profiles = Profile.objects.filter(user__id=301)

		for profile in profiles:
			conn = UpYun('ava19', 'one9', 'one9in1234')
			data = None
			if 'http' in profile.avatar.name:
				#pdb.set_trace()

				#data_img = cStringIO.StringIO(urllib2.urlopen(profile.avatar.name).read())
				data = ContentFile(urllib2.urlopen(profile.avatar.name).read())
				#data = tempfile.TemporaryFile()
				#data.write(urllib2.urlopen(profile.avatar.name).read())
				data.seek(0)
			elif 'default' in profile.avatar.name:
				continue
			else:
				try:
					profile.avatar.seek(0)
					data = profile.avatar
				except:
					print 'Warning -- Profile : %d avatar lost...' % profile.user.id
					continue
			
			conn.setContentMD5(md5file(data))

			result = conn.writeFile('%d' % profile.user.id, data)
			
			if 'http' in profile.avatar.name:
				data.close()

			if result:
				print '-- Profile : %d success...' % profile.user.id
			else:
				print 'Error -- Profile : %d ...' % profile.user.id
	
		print 'Finish.'
