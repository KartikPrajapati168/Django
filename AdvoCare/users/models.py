from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('lawyer', 'Lawyer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    # Lawyer-specific fields
    firm_name = models.CharField(max_length=200, blank=True)
    registration_no = models.CharField(max_length=50, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    # Admin might need a secret_key field (optional)
    # ...