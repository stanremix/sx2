# -*- coding:utf-8 -*-

class GuestMiddleware(object):
	def process_request(self, request):
		uid = int(request.GET.get('uid', 0))
		print 'hehe', request.GET.get('uid')
		return None
