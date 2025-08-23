from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from restaurants.models import RestaurantOwnerProfile

@receiver(post_save, sender=User)
def create_owner_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'restaurant_owner':
        RestaurantOwnerProfile.objects.get_or_create(user=instance)
        