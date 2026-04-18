# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db import models
class UserManager(BaseUserManager):

    def create_user(self,email,full_name,password=None,role='client'):
        if not email:
            raise ValueError("Email is required")
        email=self.normalize_email(email)
        user=self.model(email=email,full_name=full_name,role=role)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
    
    def create_superuser(self,email,full_name,password):
        user=self.create_user(email,full_name,password,role="admin")
        user.is_staff=True
        user.is_superuser=True
        user.save()
        return user
    
class User(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES=(
        ('client','Client'),
        ('lawfirm', 'Law Firm'),
        ('admin','Admin'),
    )
    email=models.EmailField(unique=True)
    full_name=models.CharField(max_length=255)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)

    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)

    date_joined=models.DateTimeField(auto_now_add=True)

    objects=UserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['full_name']

    def __str__(self):
        return self.email