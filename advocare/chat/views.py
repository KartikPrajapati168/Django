from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .models import ChatMessage
from cases.models import Case
from users.models import User

class SendChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        case_id = request.data.get('case_id')
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        
        if not all([case_id, receiver_id, content]):
            return Response({'error': 'Missing fields: case_id, receiver_id, content required'}, status=400)

        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)

        # Determine sender and receiver based on user role
        user = request.user
        sender_role = None
        receiver = None

        if user.role == 'client':
            # Client sending to law firm
            if case.client != user:
                return Response({'error': 'You are not authorized for this case'}, status=403)
            receiver = case.law_firm
            sender_role = 'client'
        elif user.role == 'lawfirm':
            # Law firm sending to client
            if case.law_firm != user:
                return Response({'error': 'You are not authorized for this case'}, status=403)
            receiver = case.client
            sender_role = 'lawfirm'
        else:
            return Response({'error': 'Invalid user role'}, status=403)

        # Verify receiver ID matches
        if not receiver or receiver.id != int(receiver_id):
            return Response({'error': 'Invalid receiver'}, status=400)

        # Create message
        msg = ChatMessage.objects.create(
            case=case,
            sender=user,
            receiver=receiver,
            content=content,
            sender_role=sender_role
        )
        
        return Response({
            'id': msg.id,
            'content': msg.content,
            'created_at': msg.created_at,
            'sender_role': msg.sender_role,
            'sender_name': msg.sender.full_name
        }, status=201)


class GetChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id, other_user_id):
        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)

        user = request.user
        
        # Verify access
        if user.role == 'client' and case.client != user:
            return Response({'error': 'Access denied'}, status=403)
        if user.role == 'lawfirm' and case.law_firm != user:
            return Response({'error': 'Access denied'}, status=403)

        # Get messages between these two users for this case
        messages = ChatMessage.objects.filter(
            case=case
        ).filter(
            models.Q(sender=user, receiver_id=other_user_id) |
            models.Q(sender_id=other_user_id, receiver=user)
        ).order_by('created_at')

        # Mark unread messages as read
        messages.filter(receiver=user, is_read=False).update(is_read=True)

        data = [{
            'id': m.id,
            'content': m.content,
            'sender_role': m.sender_role,
            'created_at': m.created_at,
            'sender_name': m.sender.full_name
        } for m in messages]
        
        return Response(data, status=200)


class GetConversationsView(APIView):
    """Get all conversations for the current user (grouped by case)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = []
        
        if user.role == 'client':
            # Get all cases for this client that have law firms assigned
            cases = Case.objects.filter(client=user).exclude(law_firm__isnull=True)
            for case in cases:
                # Get last message
                last_msg = ChatMessage.objects.filter(
                    case=case,
                    sender__in=[user, case.law_firm],
                    receiver__in=[user, case.law_firm]
                ).order_by('-created_at').first()
                
                # Count unread messages
                unread_count = ChatMessage.objects.filter(
                    case=case,
                    receiver=user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'case_id': case.id,
                    'case_title': case.title,
                    'other_party_id': case.law_firm.id,
                    'other_party_name': case.law_firm.full_name,
                    'other_party_role': 'lawfirm',
                    'last_message': last_msg.content if last_msg else '',
                    'last_message_time': last_msg.created_at if last_msg else None,
                    'unread_count': unread_count
                })
                
        elif user.role == 'lawfirm':
            # Get all cases assigned to this law firm
            cases = Case.objects.filter(law_firm=user).exclude(client__isnull=True)
            for case in cases:
                last_msg = ChatMessage.objects.filter(
                    case=case,
                    sender__in=[user, case.client],
                    receiver__in=[user, case.client]
                ).order_by('-created_at').first()
                
                unread_count = ChatMessage.objects.filter(
                    case=case,
                    receiver=user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'case_id': case.id,
                    'case_title': case.title,
                    'other_party_id': case.client.id,
                    'other_party_name': case.client.full_name,
                    'other_party_role': 'client',
                    'last_message': last_msg.content if last_msg else '',
                    'last_message_time': last_msg.created_at if last_msg else None,
                    'unread_count': unread_count
                })
        
        # Sort by last message time (most recent first)
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        
        return Response(conversations, status=200)