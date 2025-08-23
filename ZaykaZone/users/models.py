from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_phone = models.CharField(max_length=30, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20)
    is_google_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        # return self.full_name or self.email or "User"
        # Return the most meaningful identifier
        if self.full_name:
            return self.full_name
        if self.email:
            return self.email
        if self.phone:
            return self.phone
        return f"User #{self.pk}"
    
    # @property
    # def full_display_name(self):
    #     """For admin dropdown display"""
    #     if self.full_name:
    #         return self.full_name
    #     return self.email or self.phone or f"User #{self.pk}"
    
    # def get_full_name(self):
    #     """Return first_name plus last_name, with space in between."""
    #     full_name = f"{self.first_name} {self.last_name}"
    #     return full_name.strip()
    # ADD THIS INSTEAD:
    def get_full_name(self):
        """Return the user's full name."""
        return self.full_name
    
    def get_short_name(self):
        """Return the user's short name (first part of full name)."""
        return self.full_name.split()[0] if self.full_name else ""
    