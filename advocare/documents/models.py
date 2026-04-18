from django.db import models
from cases.models import Case
from users.models import User
from profiles.models import LawfirmProfile


class Document(models.Model):
    DOCUMENT_TYPES = (
        ('fir', 'FIR Document'),
        ('notice', 'Notice/Agreement'),
        ('evidence', 'Evidence Document'),
        ('correspondence', 'Correspondence'),
        ('id_proof', 'ID Proof'),
        # Law Firm Documents
        ('bar_council_certificate', 'Bar Council Certificate'),
        ('firm_registration', 'Firm Registration Proof'),
        ('lawyer_id_proof', 'Lawyer ID Proof'),
        ('other', 'Other'),
    )
    
    # For cases
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    # For law firm onboarding
    law_firm = models.ForeignKey(LawfirmProfile, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    file = models.FileField(upload_to='documents/')
    doc_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file_name = models.CharField(max_length=255, blank=True, default='')
    file_size = models.IntegerField(default=0)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.file.name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
        super().save(*args, **kwargs)