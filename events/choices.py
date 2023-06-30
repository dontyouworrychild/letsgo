from django.db import models


class EventStatus(models.TextChoices):
    PARTICIPATED = 'participated', 'Participated',
    REGISTERED = 'registered', 'Registered',
    UNREGISTERED = 'unregistered', 'Unregistered'


class EventType(models.TextChoices):
    PRIVATE = 'private', 'Private',
    PUBLIC = 'public', 'Public'


class PublicEventStatus(models.TextChoices):
    WAITING = 'waiting', 'Waiting',
    ACCEPTED = 'accepted', 'Accepted',
    REJECTED = 'rejected', 'Rejected'
