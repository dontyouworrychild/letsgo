from users.serializers import NotificationSerializer


def send_notification(event, message):
    notification_data = {
        'recipient': event.created_by.id,
        'message': message,
    }
    notification_serializer = NotificationSerializer(data=notification_data)
    notification_serializer.is_valid(raise_exception=True)
    notification_serializer.save()
