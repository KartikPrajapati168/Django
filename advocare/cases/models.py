# from django.db import models
# from users.models import User
# # Create your models here.
# class Case(models.Model):
#     STATUS_CHOICES=(
#         ('open','Open'),
#         ('in_progress','In Progress'),
#         ('closed','Closed'),
#     )
#     URGENCY_CHOICES=(
#         ('low','Low'),
#         ('medium','Medium'),
#         ('high','High'),
#     )
#     client=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cases')
#     case_type=models.CharField(max_length=255)
#     title=models.CharField(max_length=255)
#     description=models.TextField()
#     urgency=models.CharField(max_length=10,choices=URGENCY_CHOICES)
#     status=models.CharField(max_length=15,choices=STATUS_CHOICES,default='open')
#     created_at=models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} - {self.client.full_name}"





from django.db import models
from users.models import User


class Case(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    URGENCY_CHOICES = (
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    CASE_TYPE_CHOICES = (
        ('criminal', 'Criminal Law'),
        ('civil', 'Civil Law'),
        ('family', 'Family Law'),
        ('corporate', 'Corporate Law'),
        ('property', 'Property Law'),
        ('tax', 'Tax Law'),
        ('employment', 'Employment Law'),
        ('intellectual', 'Intellectual Property'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    law_firm = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    
    # Case Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    case_type = models.CharField(max_length=50, choices=CASE_TYPE_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Court Details
    court_location = models.CharField(max_length=255, blank=True, null=True)
    opposing_party = models.CharField(max_length=255, blank=True, null=True)
    filing_deadline = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.client.full_name}"
    

class CourtUpdate(models.Model):
    UPDATE_TYPES = (
        ('hearing', 'Hearing'),
        ('order', 'Court Order'),
        ('update', 'General Update'),
    )
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='court_updates')
    title = models.CharField(max_length=255)
    description = models.TextField()
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default='update')
    date = models.DateTimeField()
    court_name = models.CharField(max_length=255, blank=True)
    priority = models.CharField(max_length=10, choices=(('low','Low'),('normal','Normal'),('high','High')), default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.case.title}"
    

class Dispute(models.Model):
    STATUS_CHOICES = (('open', 'Open'), ('resolved', 'Resolved'), ('closed', 'Closed'))
    filed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filed_disputes')
    against = models.ForeignKey(User, on_delete=models.CASCADE, related_name='against_disputes')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    