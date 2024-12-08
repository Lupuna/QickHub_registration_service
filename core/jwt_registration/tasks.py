from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_verification_email(subject, message, from_email, recipient_list, auth_user, auth_password):
    send_mail(subject, message, from_email,
              recipient_list, auth_user, auth_password)
