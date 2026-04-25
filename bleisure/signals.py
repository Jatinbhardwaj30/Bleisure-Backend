from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserEventInterest, UserEventReview, Event


@receiver(post_save, sender=UserEventInterest)
def increment_interested_count(sender, instance, created, **kwargs):
    """
    Increment interested_count when a new UserEventInterest is created.
    More efficient than recalculating every time.
    """
    if created:
        event = instance.event
        event.interested_count = event.interested_users.count()
        event.save(update_fields=['interested_count'])


@receiver(post_delete, sender=UserEventInterest)
def decrement_interested_count(sender, instance, **kwargs):
    """
    Decrement interested_count when a UserEventInterest is deleted.
    """
    event = instance.event
    event.interested_count = max(0, event.interested_users.count())
    event.save(update_fields=['interested_count'])


@receiver(post_save, sender=UserEventReview)
def update_event_rating(sender, instance, created, **kwargs):
    """
    Update event rating when a review is created or updated.
    Recalculates average rating from all reviews.
    """
    event = instance.event
    event.rating = event.get_average_rating()
    event.save(update_fields=['rating'])


@receiver(post_delete, sender=UserEventReview)
def recalculate_event_rating_on_delete(sender, instance, **kwargs):
    """
    Recalculate event rating when a review is deleted.
    """
    event = instance.event
    event.rating = event.get_average_rating()
    event.save(update_fields=['rating'])
