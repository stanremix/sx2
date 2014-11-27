from django.contrib import admin
from people.models import Profile, Feedback, Relation

class ProfileAdmin(admin.ModelAdmin):
	pass

admin.site.register(Profile, ProfileAdmin)

class FeedbackAdmin(admin.ModelAdmin):
	pass

admin.site.register(Feedback, FeedbackAdmin)

class RelationAdmin(admin.ModelAdmin):
	pass

admin.site.register(Relation, RelationAdmin)
