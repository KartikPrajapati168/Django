from django.db import models
from users.models import User
# Create your models here.
class Case(models.Model):
    STATUS_CHOICES=(
        ('open','Open'),
        ('in_progress','In Progress'),
        ('closed','Closed'),
    )
    URGENCY_CHOICES=(
        ('low','Low'),
        ('medium','Medium'),
        ('high','High'),
    )
    client=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cases')
    case_type=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    description=models.TextField()
    urgency=models.CharField(max_length=10,choices=URGENCY_CHOICES)
    status=models.CharField(max_length=15,choices=STATUS_CHOICES,default='open')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.client.full_name}"
    
