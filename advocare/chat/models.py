from django.db import models
from users.models import User
from cases.models import Case

class ChatMessage(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    sender_role = models.CharField(max_length=20, choices=(
        ('client', 'Client'),
        ('lawfirm', 'Law Firm'),
        ('admin', 'Admin'),
    ), default='client')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat from {self.sender.full_name} on case {self.case.title}"