from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(
            user=instance,
            name=instance.username,
            email=instance.email
        )

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject="Welcome to SwiftCart!",
            message=f"Hi {instance.username},\n\nThanks for creating an account with SwiftCart. We're excited to have you!\n\nHappy shopping,\nThe SwiftCart Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )      
