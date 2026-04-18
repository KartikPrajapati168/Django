from django.db import models
from users.models import User


class ClientProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clientprofile')
    
    # Contact
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Personal
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # ID Proof
    id_proof_type = models.CharField(max_length=50, blank=True, null=True)
    id_proof_number = models.CharField(max_length=100, blank=True, null=True)
    id_proof_issue_date = models.DateField(null=True, blank=True)
    id_proof_expiry_date = models.DateField(null=True, blank=True)
    id_proof_document_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Consent
    terms_accepted = models.BooleanField(default=False)
    data_consent = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_onboarded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - Client"


class LawfirmProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('not_submitted', 'Not Submitted')
    ]
    
    # Experience level choices
    EXPERIENCE_CHOICES = (
        ('0-2', '0-2 years'),
        ('3-5', '3-5 years'),
        ('6-10', '6-10 years'),
        ('11-15', '11-15 years'),
        ('15+', '15+ years'),
    )
    
    SPECIALIZATION_CHOICES = (
        ('corporate', 'Corporate Law'),
        ('criminal', 'Criminal Law'),
        ('family', 'Family Law'),
        ('intellectual', 'Intellectual Property'),
        ('tax', 'Tax Law'),
        ('labor', 'Labor Law'),
        ('civil', 'Civil Litigation'),
        ('immigration', 'Immigration Law'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawfirmprofile')
    
    # Firm Details
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    registration_no = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Firm Experience & Specialization (NEW FIELDS)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)  # Comma separated or single
    
    # Primary Lawyer Details
    primary_lawyer_name = models.CharField(max_length=255, blank=True, null=True)
    primary_lawyer_bar_council_id = models.CharField(max_length=100, blank=True, null=True)
    primary_lawyer_years_experience = models.IntegerField(null=True, blank=True)
    primary_lawyer_specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, blank=True, null=True)
    
    # Firm Statistics
    total_lawyers = models.IntegerField(default=0)
    total_cases_handled = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_onboarded = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.firm_name} - Law Firm" if self.firm_name else f"{self.user.email}"


class TeamMember(models.Model):
    ROLE_CHOICES = (
        ('partner', 'Partner'),
        ('senior_advocate', 'Senior Advocate'),
        ('associate', 'Associate'),
        ('legal_assistant', 'Legal Assistant'),
        ('paralegal', 'Paralegal'),
    )
    
    law_firm = models.ForeignKey(LawfirmProfile, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    experience_years = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminprofile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    secret_key_verified = models.BooleanField(default=False)
    secret_key_hash = models.CharField(max_length=128, blank=True, null=True)
    dashboard_theme = models.CharField(max_length=50, default="light")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    def set_secret_key(self, raw_key):
        from django.contrib.auth.hashers import make_password
        self.secret_key_hash = make_password(raw_key)
        self.secret_key_verified = True
        self.save()

    def check_secret_key(self, raw_key):
        from django.contrib.auth.hashers import check_password
        if not self.secret_key_hash:
            return False
        return check_password(raw_key, self.secret_key_hash)