from django.contrib import admin

from .models import User, FriendRequest, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(FriendRequest)
admin.site.register(Notification)
