import uuid
from datetime import datetime, timezone

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from .enums import TOKEN_TYPE_CHOICE, ROLE_CHOICE


def default_role():
    return ["CUSTOMER"]


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _("email address"), null=True, blank=True, unique=True)
    password = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.FileField(upload_to="users/")
    
    connected_ids = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=True, blank=True, null=True)
    proficient = models.ManyToManyField()
    location = models.CharField()
    goals = models.ManyToManyField()

    is_locked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    REQUIRED_FIELDS = []
    roles = ArrayField(models.CharField(max_length=20, blank=True,
                                        choices=ROLE_CHOICE), default=default_role, size=6)
    

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=8)
    token_type = models.CharField(max_length=100, choices=TOKEN_TYPE_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def is_valid(self) -> bool:
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60 )
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def reset_user_password(self, password: str) -> None:
        self.user.set_password(password)
        self.user.save()