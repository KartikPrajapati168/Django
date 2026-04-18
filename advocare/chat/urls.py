from django.urls import path
from .views import SendChatView, GetChatsView, GetConversationsView

urlpatterns = [
    path('send/', SendChatView.as_view(), name='send-chat'),
    path('<int:case_id>/<int:other_user_id>/', GetChatsView.as_view(), name='get-chats'),
    path('conversations/', GetConversationsView.as_view(), name='get-conversations'),
]