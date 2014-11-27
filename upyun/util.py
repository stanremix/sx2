# -*- coding: utf8 -*-
from django.contrib.auth.models import User
import os
import sys
import pdb
import urllib2
import Image
import cStringIO
import tempfile

from upyun import UpYun,md5,md5file
from django.core.files.base import ContentFile
#from upyun import UpYun
import upyun
#import pdb

def upload_pic(pic, code, up_type='ava'):
	#pdb.set_trace()

	try:
		ext_name = ''
		if up_type == 'ava':
			conn = UpYun('one9inava', 'one9', 'one9in1234')
		elif up_type == 'vid':
			conn = UpYun('vid19', 'one9', 'one9in1234')
			ext_name = '_cpp.mp4'
		elif up_type == 'avd':
			conn = UpYun('vid19', 'one9', 'one9in1234')
			ext_name = '_ava.mp4'
		else:
			conn = UpYun('cpp19', 'one9', 'one9in1234')

		if 'http' in pic.name:
			data = ContentFile(urllib2.urlopen(pic.name).read())	
			data.seek(0)
		elif 'default' in pic.name:
			return True
		else:
			try:
				pic.seek(0)
				data = pic
			except:
				print 'no pic'
				return False
			#conn.setContentMD5(md5file(pic))
			#result = conn.writeFile('%d' % code, pic)
			#data.write(pic.read())
			#data.seek(0)

		conn.setContentMD5(md5file(data))

		#result = conn.deleteFile('%d' % code)
		result = conn.writeFile('%s%s' % (code, ext_name), data)
		
		print result
		data.close()
		if result:
			print 'ok!!'
			return True
		else:
			print 'nok'
			return False
	except Exception, ex:
		print Exception,":",ex
		return False

