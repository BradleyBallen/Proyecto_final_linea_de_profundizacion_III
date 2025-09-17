from django.contrib import admin
from .models import Level, Lesson, UserProfile, LevelMembership, Conversation, Message, Progress

admin.site.register(Level)
admin.site.register(Lesson)
admin.site.register(UserProfile)
admin.site.register(LevelMembership)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Progress)
