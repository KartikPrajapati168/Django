from django.db import models
from cases.models import Case
# Create your models here.
class Document(models.Model):
    case=models.ForeignKey(Case,on_delete=models.CASCADE,related_name='documents')
    file=models.FileField(upload_to='documents/')
    doc_type=models.CharField(max_length=100)
    uploaded_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_type} - {self.case.title}"
    
    