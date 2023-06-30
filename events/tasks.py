import os
from celery import shared_task
from rest_framework.views import Response
from django.core.mail import send_mail, get_connection


@shared_task
def send_payment_confirmation(user_id):
    email_host_user = os.environ.get('EMAIL_HOST_USER')
    email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')
    try:
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=email_host_user,
            password=email_host_password,
            use_tls=True,
            use_ssl=False
        )
        send_mail(
            subject="Payment confirmation async",
            message="Your payment successfully processed",
            from_email=email_host_user,
            recipient_list=['xyzxyz@gmail.com'],
            connection=connection,
        )
    # except SMTPSenderRefused as e:
    #     error = e.smtp_error
    #     if isinstance(error, bytes):
    #         for coding in ('gbk', 'utf8'):
    #             try:
    #                 error = error.decode(coding)
    #             except UnicodeDecodeError:
    #                 continue
    #             else:
    #                 break
    #     return Response({"error": str(error)}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
