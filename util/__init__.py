from django.http import HttpResponse
from django.utils import simplejson

class HttpAjaxResponse(HttpResponse):
	def __init__(self, content={}, mimetype=None, status=None, content_type='application/json'):
		content = simplejson.dumps(content)
		super(HttpAjaxResponse, self).__init__(content, mimetype=mimetype, status=status, content_type=content_type)
