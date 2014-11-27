# -*- coding:utf-8 -*-
from django.contrib import admin
from message.models import Message, MessageToUser

class MessageAdmin(admin.ModelAdmin):
	pass

admin.site.register(Message, MessageAdmin)

class MessageToUserAdmin(admin.ModelAdmin):
	pass

admin.site.register(MessageToUser, MessageToUserAdmin)

