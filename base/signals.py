from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Room, Notification, Selected

@receiver(post_save, sender=Room)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        followers = instance.recruiter.followers.all()
        for follower in followers:
            Notification.objects.create(user=follower, room=instance, notification_type = 'room')

@receiver(post_save, sender=Selected)
def accepted_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user = instance.applicant, room=instance.opportunity, notification_type = 'selected')