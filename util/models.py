# -*- coding:utf-8 -*-
from django.db import models

# Create your models here.
class DefaultModel(models.Model):
	is_valid = models.BooleanField(default=True)
	tag = models.IntegerField(null=True, blank=True)
	create_time = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		abstract = True

