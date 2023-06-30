from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import FriendRequestStatus


class User(AbstractUser):
    friends = models.ManyToManyField('User', symmetrical=True, blank=True, null=True)

    def __str__(self):
        return self.username


class FriendRequest(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendrequest_received')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendrequest_sent')
    status = models.CharField(max_length=20, choices=FriendRequestStatus.choices, default='pending')


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
