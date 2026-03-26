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

class AdminProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=20,blank=True,null=True)
    secret_key_verified=models.BooleanField(default=False)
    dashboard_theme=models.CharField(max_length=50,default="light")
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
