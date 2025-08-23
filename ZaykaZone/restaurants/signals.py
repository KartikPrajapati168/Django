from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from restaurants.models import RestaurantOwnerProfile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            RestaurantOwnerProfile.objects.create(user=instance)
        except Exception as e:
            print("❌ Profile create failed:", e)
            
