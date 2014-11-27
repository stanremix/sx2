# -*- coding:utf-8 -*-
from django.contrib import admin
from topic.models import Topic, Category, UserFollowTopic

class TopicAdmin(admin.ModelAdmin):
	pass

admin.site.register(Topic, TopicAdmin)

class CategoryAdmin(admin.ModelAdmin):
	pass

admin.site.register(Category, CategoryAdmin)

class UserFollowTopicAdmin(admin.ModelAdmin):
	pass

admin.site.register(UserFollowTopic, UserFollowTopicAdmin)
