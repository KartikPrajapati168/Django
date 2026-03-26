from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from profiles.models import ClientProfile,LawfirmProfile,AdminProfile

@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created, **kwargs):
    if created:
        if instance.role=="client":
            ClientProfile.objects.create(User=instance)
        elif instance.role=="lawfirm":
            LawfirmProfile.objects.create(User=instance)
        elif instance.role == 'admin':
            AdminProfile.objects.create(user=instance)