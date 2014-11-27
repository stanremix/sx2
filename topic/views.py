# Create your views here.

from django.http import HttpResponse
from util import HttpAjaxResponse
from topic.models import Topic
import datetime

def topic(request):
	return HttpAjaxResponse(content=dict(data=Topic.objects._all()))
	

