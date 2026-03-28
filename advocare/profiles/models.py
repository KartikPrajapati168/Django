# Create your models here.
from django.db import models
from users.models import User

class ClientProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15)
    city=models.CharField(max_length=100)

     # 🔥 NEW FIELDS
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_onboarded = models.BooleanField(default=False)

    # ✅ OPTIONAL (Recommended)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - Client" 

class LawfirmProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    firm_name=models.CharField(max_length=255)
    phone=models.CharField(max_length=15)
    registration_no=models.CharField(max_length=100)
    experience=models.IntegerField()
    specialization=models.CharField(max_length=255)

    # 🔥 NEW FIELDS
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_onboarded = models.BooleanField(default=False)

    # ✅ OPTIONAL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - Law Firm" 

from django.contrib.auth.hashers import make_password, check_password

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    secret_key_verified = models.BooleanField(default=False)
    secret_key_hash = models.CharField(max_length=128, blank=True, null=True)   # new field
    dashboard_theme = models.CharField(max_length=50, default="light")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def set_secret_key(self, raw_key):
        """Hash and store the secret key."""
        self.secret_key_hash = make_password(raw_key)
        self.secret_key_verified = True
        self.save()

    def check_secret_key(self, raw_key):
        """Verify the provided secret key against the stored hash."""
        if not self.secret_key_hash:
            return False
        return check_password(raw_key, self.secret_key_hash)
