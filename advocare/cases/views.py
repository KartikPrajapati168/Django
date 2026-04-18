# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Case
# from users.models import User


# class MyCasesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         cases = Case.objects.filter(client=request.user).order_by('-created_at')
#         data = []
#         for case in cases:
#             data.append({
#                 'id': case.id,
#                 'title': case.title,
#                 'description': case.description,
#                 'case_type': case.case_type,
#                 'status': case.status,
#                 'urgency': case.urgency,
#                 'court_location': case.court_location,
#                 'opposing_party': case.opposing_party,
#                 'filing_deadline': case.filing_deadline,
#                 'law_firm_name': case.law_firm.full_name if case.law_firm else None,
#                 'law_firm_id': case.law_firm.id if case.law_firm else None,
#                 'created_at': case.created_at,
#                 'updated_at': case.updated_at,
#             })
#         return Response({
#             'status': 'success',
#             'data': data,
#             'count': len(data)
#         }, status=status.HTTP_200_OK)


# class CaseListCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         cases = Case.objects.filter(client=request.user)
#         data = []
#         for case in cases:
#             data.append({
#                 'id': case.id,
#                 'title': case.title,
#                 'case_type': case.case_type,
#                 'status': case.status,
#                 'created_at': case.created_at,
#             })
#         return Response(data, status=status.HTTP_200_OK)

#     def post(self, request):
#         try:
#             # Get only valid fields from request
#             case = Case.objects.create(
#                 client=request.user,
#                 title=request.data.get('title', ''),
#                 case_type=request.data.get('case_type', ''),
#                 description=request.data.get('description', ''),
#                 urgency=request.data.get('urgency', 'normal'),
#                 court_location=request.data.get('court_location', ''),
#                 opposing_party=request.data.get('opposing_party', ''),
#                 filing_deadline=request.data.get('filing_deadline', None),
#                 status='pending'
#             )
            
#             return Response({
#                 'id': case.id,
#                 'title': case.title,
#                 'message': 'Case created successfully'
#             }, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)


# class CaseDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk):
#         try:
#             case = Case.objects.get(id=pk, client=request.user)
#             data = {
#                 'id': case.id,
#                 'title': case.title,
#                 'description': case.description,
#                 'case_type': case.case_type,
#                 'status': case.status,
#                 'urgency': case.urgency,
#                 'court_location': case.court_location,
#                 'opposing_party': case.opposing_party,
#                 'filing_deadline': case.filing_deadline,
#                 'law_firm_name': case.law_firm.full_name if case.law_firm else None,
#                 'created_at': case.created_at,
#                 'updated_at': case.updated_at,
#             }
#             return Response(data, status=status.HTTP_200_OK)
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)


# class AssignCaseView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):
#         try:
#             case = Case.objects.get(id=pk, client=request.user)
#             law_firm_id = request.data.get('law_firm_id')
            
#             if not law_firm_id:
#                 return Response({'error': 'law_firm_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
#             try:
#                 law_firm = User.objects.get(id=law_firm_id, role='lawfirm')
#                 case.law_firm = law_firm
#                 case.law_firm_name = law_firm.full_name
#                 case.status = 'assigned'
#                 case.save()
                
#                 return Response({
#                     'status': 'success',
#                     'message': f'Case assigned to {law_firm.full_name}'
#                 }, status=status.HTTP_200_OK)
                
#             except User.DoesNotExist:
#                 return Response({'error': 'Law firm not found'}, status=status.HTTP_404_NOT_FOUND)
                
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
        


# # cases/views.py (add these classes)

# class CaseDetailUpdateView(APIView):
#     """Get full case details or update case fields (PATCH)."""
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk):
#         try:
#             case = Case.objects.get(id=pk, client=request.user)
#             data = {
#                 'id': case.id,
#                 'title': case.title,
#                 'description': case.description,
#                 'case_type': case.case_type,
#                 'status': case.status,
#                 'urgency': case.urgency,
#                 'court_location': case.court_location,
#                 'opposing_party': case.opposing_party,
#                 'filing_deadline': case.filing_deadline,
#                 'law_firm_name': case.law_firm.full_name if case.law_firm else None,
#                 'law_firm_id': case.law_firm.id if case.law_firm else None,
#                 'created_at': case.created_at,
#                 'updated_at': case.updated_at,
#                 'documents': []  # documents will be fetched separately or you can include
#             }
#             # Optionally include documents
#             from documents.models import Document
#             docs = Document.objects.filter(case=case)
#             data['documents'] = [{
#                 'id': d.id,
#                 'file_name': d.file_name,
#                 'file_url': d.file.url,
#                 'doc_type': d.doc_type,
#                 'uploaded_at': d.uploaded_at
#             } for d in docs]
#             return Response(data, status=200)
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=404)

#     def patch(self, request, pk):
#         try:
#             case = Case.objects.get(id=pk, client=request.user)
#             # Update only allowed fields
#             allowed_fields = ['title', 'description', 'case_type', 'urgency',
#                               'court_location', 'opposing_party', 'filing_deadline']
#             for field in allowed_fields:
#                 if field in request.data:
#                     setattr(case, field, request.data[field])
#             case.save()
#             return Response({'message': 'Case updated successfully'}, status=200)
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=404)
        

# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from .models import Case
# from users.models import User

# class PendingCaseRequestsView(APIView):
#     """Law firm sees cases assigned to them with status='assigned'"""
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.role != 'lawfirm':
#             return Response({'error': 'Law firm access required'}, status=403)
        
#         # Cases assigned to this law firm but not yet accepted
#         cases = Case.objects.filter(
#             law_firm=request.user,
#             status='assigned'
#         ).exclude(status='in_progress')
        
#         data = []
#         for case in cases:
#             data.append({
#                 'id': case.id,
#                 'title': case.title,
#                 'case_type': case.case_type,
#                 'description': case.description,
#                 'urgency': case.urgency,
#                 'court_location': case.court_location,
#                 'client_name': case.client.full_name,
#                 'client_email': case.client.email,
#                 'client_phone': getattr(case.client.clientprofile, 'phone', ''),
#                 'created_at': case.created_at,
#                 'documents': [{'id': d.id, 'file_name': d.file_name} for d in case.documents.all()]
#             })
#         return Response(data)

# class AcceptCaseRequestView(APIView):
#     """Law firm accepts a case request"""
#     permission_classes = [IsAuthenticated]

#     def post(self, request, case_id):
#         try:
#             case = Case.objects.get(id=case_id, law_firm=request.user, status='assigned')
#             case.status = 'in_progress'
#             case.save()
            
#             # Create notification for client
#             from notifications.models import Notification
#             Notification.objects.create(
#                 user=case.client,
#                 message=f"Law firm {request.user.full_name} has accepted your case: {case.title}",
#                 is_read=False
#             )
            
#             return Response({'message': 'Case accepted successfully'})
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=404)

# class RejectCaseRequestView(APIView):
#     """Law firm rejects a case request"""
#     permission_classes = [IsAuthenticated]

#     def post(self, request, case_id):
#         try:
#             case = Case.objects.get(id=case_id, law_firm=request.user, status='assigned')
#             case.status = 'pending'  # Back to pending
#             case.law_firm = None
#             case.law_firm_name = None
#             case.save()
            
#             # Notify client
#             from notifications.models import Notification
#             Notification.objects.create(
#                 user=case.client,
#                 message=f"Law firm {request.user.full_name} has declined your case: {case.title}",
#                 is_read=False
#             )
            
#             return Response({'message': 'Case request rejected'})
#         except Case.DoesNotExist:
#             return Response({'error': 'Case not found'}, status=404)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Case
from users.models import User


class MyCasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cases = Case.objects.filter(client=request.user).order_by('-created_at')
        data = []
        for case in cases:
            data.append({
                'id': case.id,
                'title': case.title,
                'description': case.description,
                'case_type': case.case_type,
                'status': case.status,
                'urgency': case.urgency,
                'court_location': case.court_location,
                'opposing_party': case.opposing_party,
                'filing_deadline': case.filing_deadline,
                'law_firm_name': case.law_firm.full_name if case.law_firm else None,
                'law_firm_id': case.law_firm.id if case.law_firm else None,
                'created_at': case.created_at,
                'updated_at': case.updated_at,
            })
        return Response({
            'status': 'success',
            'data': data,
            'count': len(data)
        }, status=status.HTTP_200_OK)


class CaseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cases = Case.objects.filter(client=request.user)
        data = []
        for case in cases:
            data.append({
                'id': case.id,
                'title': case.title,
                'case_type': case.case_type,
                'status': case.status,
                'created_at': case.created_at,
            })
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            case = Case.objects.create(
                client=request.user,
                title=request.data.get('title', ''),
                case_type=request.data.get('case_type', ''),
                description=request.data.get('description', ''),
                urgency=request.data.get('urgency', 'normal'),
                court_location=request.data.get('court_location', ''),
                opposing_party=request.data.get('opposing_party', ''),
                filing_deadline=request.data.get('filing_deadline', None),
                status='pending'
            )
            return Response({
                'id': case.id,
                'title': case.title,
                'message': 'Case created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CaseDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            case = Case.objects.get(id=pk, client=request.user)
            data = {
                'id': case.id,
                'title': case.title,
                'description': case.description,
                'case_type': case.case_type,
                'status': case.status,
                'urgency': case.urgency,
                'court_location': case.court_location,
                'opposing_party': case.opposing_party,
                'filing_deadline': case.filing_deadline,
                'law_firm_name': case.law_firm.full_name if case.law_firm else None,
                'law_firm_id': case.law_firm.id if case.law_firm else None,
                'created_at': case.created_at,
                'updated_at': case.updated_at,
                'documents': []
            }
            from documents.models import Document
            docs = Document.objects.filter(case=case)
            data['documents'] = [{
                'id': d.id,
                'file_name': d.file_name,
                'file_url': d.file.url,
                'doc_type': d.doc_type,
                'uploaded_at': d.uploaded_at
            } for d in docs]
            return Response(data, status=200)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)

    def patch(self, request, pk):
        try:
            case = Case.objects.get(id=pk, client=request.user)
            allowed_fields = ['title', 'description', 'case_type', 'urgency',
                              'court_location', 'opposing_party', 'filing_deadline']
            for field in allowed_fields:
                if field in request.data:
                    setattr(case, field, request.data[field])
            case.save()
            return Response({'message': 'Case updated successfully'}, status=200)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)


class AssignCaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            case = Case.objects.get(id=pk, client=request.user)
            law_firm_id = request.data.get('law_firm_id')
            if not law_firm_id:
                return Response({'error': 'law_firm_id required'}, status=400)
            try:
                law_firm = User.objects.get(id=law_firm_id, role='lawfirm')
                case.law_firm = law_firm
                case.law_firm_name = law_firm.full_name
                case.status = 'assigned'
                case.save()
                return Response({
                    'status': 'success',
                    'message': f'Case assigned to {law_firm.full_name}'
                }, status=200)
            except User.DoesNotExist:
                return Response({'error': 'Law firm not found'}, status=404)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)


class PendingCaseRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'lawfirm':
            return Response({'error': 'Law firm access required'}, status=403)
        cases = Case.objects.filter(law_firm=request.user, status='assigned').exclude(status='in_progress')
        data = []
        for case in cases:
            data.append({
                'id': case.id,
                'title': case.title,
                'case_type': case.case_type,
                'description': case.description,
                'urgency': case.urgency,
                'court_location': case.court_location,
                'client_name': case.client.full_name,
                'client_email': case.client.email,
                'client_phone': getattr(case.client.clientprofile, 'phone', ''),
                'created_at': case.created_at,
                'documents': [{'id': d.id, 'file_name': d.file_name} for d in case.documents.all()]
            })
        return Response(data)


class AcceptCaseRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, case_id):
        try:
            case = Case.objects.get(id=case_id, law_firm=request.user, status='assigned')
            case.status = 'in_progress'
            case.save()
            # Notification removed – you can add your own logic later
            print(f"✅ Case {case.id} accepted by {request.user.full_name}")
            return Response({'message': 'Case accepted successfully'})
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)


class RejectCaseRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, case_id):
        try:
            case = Case.objects.get(id=case_id, law_firm=request.user, status='assigned')
            case.status = 'pending'
            case.law_firm = None
            case.law_firm_name = None
            case.save()
            print(f"❌ Case {case.id} rejected by {request.user.full_name}")
            return Response({'message': 'Case request rejected'})
        except Case.DoesNotExist:
            return Response({'error': 'Case not found'}, status=404)
        

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from .models import Case, CourtUpdate
from .serializers import CaseSerializer, CourtUpdateSerializer, TeamMemberSerializer
from profiles.models import LawfirmProfile, TeamMember

# Helper
def get_lawfirm_user(request):
    return request.user  # assuming User instance

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lawfirm_stats(request):
    user = get_lawfirm_user(request)
    # Get all cases where this law firm is assigned
    cases = Case.objects.filter(law_firm=user)
    total = cases.count()
    active = cases.filter(status='in_progress').count()
    pending_requests = cases.filter(status='assigned').count()  # assigned but not yet accepted
    # Success rate calculation example (you can change logic)
    resolved = cases.filter(status='resolved').count()
    success_rate = round((resolved / total * 100) if total > 0 else 0, 1)
    data = {
        'totalCases': total,
        'activeCases': active,
        'pendingRequests': pending_requests,
        'successRate': success_rate,
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_requests(request):
    """Cases assigned to this firm with status='assigned' (waiting for firm to accept)"""
    user = get_lawfirm_user(request)
    cases = Case.objects.filter(law_firm=user, status='assigned')
    serializer = CaseSerializer(cases, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_case(request, case_id):
    user = get_lawfirm_user(request)
    try:
        case = Case.objects.get(id=case_id, law_firm=user, status='assigned')
        case.status = 'in_progress'
        case.save()
        return Response({'status': 'accepted'})
    except Case.DoesNotExist:
        return Response({'error': 'Case not found or not assignable'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_case(request, case_id):
    user = get_lawfirm_user(request)
    try:
        case = Case.objects.get(id=case_id, law_firm=user, status='assigned')
        case.law_firm = None
        case.status = 'pending'   # back to pool
        case.save()
        return Response({'status': 'rejected'})
    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_cases(request):
    """All cases where law_firm = current user (any status)"""
    user = get_lawfirm_user(request)
    cases = Case.objects.filter(law_firm=user)
    serializer = CaseSerializer(cases, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accepted_cases(request):
    """Cases with status='in_progress' for this firm"""
    user = get_lawfirm_user(request)
    cases = Case.objects.filter(law_firm=user, status='in_progress')
    serializer = CaseSerializer(cases, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lawfirm_lawyers(request):
    """List of TeamMember under this law firm"""
    try:
        profile = LawfirmProfile.objects.get(user=request.user)
    except LawfirmProfile.DoesNotExist:
        return Response([], status=200)
    lawyers = TeamMember.objects.filter(law_firm=profile)
    serializer = TeamMemberSerializer(lawyers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_lawyer(request):
    """Add a TeamMember to this law firm"""
    try:
        profile = LawfirmProfile.objects.get(user=request.user)
    except LawfirmProfile.DoesNotExist:
        return Response({'error': 'Law firm profile not found'}, status=400)
    data = request.data.copy()
    data['law_firm'] = profile.id
    serializer = TeamMemberSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def court_updates(request):
    """Return court updates for cases belonging to this law firm"""
    user = get_lawfirm_user(request)
    case_ids = Case.objects.filter(law_firm=user).values_list('id', flat=True)
    updates = CourtUpdate.objects.filter(case_id__in=case_ids).order_by('-date')
    serializer = CourtUpdateSerializer(updates, many=True)
    return Response(serializer.data)


from datetime import datetime
from django.db.models.functions import ExtractMonth

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_case_stats(request):
    user = request.user
    cases = Case.objects.filter(law_firm=user)
    year = datetime.now().year
    new_cases = cases.filter(created_at__year=year).annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
    closed_cases = cases.filter(status__in=['closed','resolved'], updated_at__year=year).annotate(month=ExtractMonth('updated_at')).values('month').annotate(count=Count('id')).order_by('month')
    new_data = [0]*12
    closed_data = [0]*12
    for item in new_cases:
        new_data[item['month']-1] = item['count']
    for item in closed_cases:
        closed_data[item['month']-1] = item['count']
    return Response({'new_cases': new_data, 'closed_cases': closed_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_case(request, case_id):
    try:
        case = Case.objects.get(id=case_id, law_firm=request.user)
        case.status = 'closed'
        case.save()
        return Response({'status': 'closed'})
    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, status=404)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_team_member(request, member_id):
    try:
        member = TeamMember.objects.get(id=member_id, law_firm__user=request.user)
        member.delete()
        return Response({'status': 'deleted'})
    except TeamMember.DoesNotExist:
        return Response({'error': 'Team member not found'}, status=404)
    

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Case, CourtUpdate, Dispute
from .serializers import CourtUpdateSerializer
from users.models import User

# ---------- ADMIN: all cases ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_cases(request):
    """Return all cases in the system (for admin)"""
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    
    cases = Case.objects.select_related('client', 'law_firm').all().order_by('-created_at')
    data = []
    for case in cases:
        data.append({
            'id': case.id,
            'title': case.title,
            'description': case.description,
            'case_type': case.case_type,
            'status': case.status,
            'urgency': case.urgency,
            'court_location': case.court_location,
            'opposing_party': case.opposing_party,
            'filing_deadline': case.filing_deadline,
            'client_name': case.client.full_name,
            'client_email': case.client.email,
            'lawfirm_name': case.law_firm.full_name if case.law_firm else None,
            'created_at': case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': case.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return Response(data)


# ---------- ADMIN: all assigned cases (cases with a law firm) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_assigned_all(request):
    """Return all cases that have been assigned to any law firm"""
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    
    cases = Case.objects.filter(law_firm__isnull=False).select_related('client', 'law_firm').order_by('-updated_at')
    data = []
    for case in cases:
        data.append({
            'id': case.id,
            'title': case.title,
            'case_type': case.case_type,
            'status': case.status,
            'client_name': case.client.full_name,
            'lawfirm_name': case.law_firm.full_name if case.law_firm else None,
            'court_location': case.court_location,
            'assigned_at': case.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return Response(data)


# ---------- ADMIN: send court update (to a specific case's law firm) ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_court_update(request):
    """Admin creates a court update and it is linked to a case"""
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    
    # Expected fields: case_id, title, description, update_type, court_name, date, priority
    case_id = request.data.get('case_id')
    if not case_id:
        return Response({'error': 'case_id is required'}, status=400)
    
    try:
        case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, status=404)
    
    # Create court update
    update = CourtUpdate.objects.create(
        case=case,
        title=request.data.get('title', ''),
        description=request.data.get('description', ''),
        update_type=request.data.get('type', 'update'),  # 'type' from frontend, map to update_type
        court_name=request.data.get('court_name', ''),
        date=request.data.get('date', None),
        priority=request.data.get('priority', 'normal'),
    )
    
    # Optional: send notification to law firm (you can implement later)
    
    return Response({
        'id': update.id,
        'message': 'Court update sent successfully'
    }, status=201)


# ---------- ADMIN: disputes (already provided, but keep here for completeness) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_disputes(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    try:
        disputes = Dispute.objects.all().order_by('-created_at')
        data = [{
            'id': d.id,
            'subject': d.subject,
            'description': d.description,
            'status': d.status,
            'category': d.category,
            'filed_by_name': d.filed_by.full_name if d.filed_by else '',
            'against_name': d.against.full_name if d.against else '',
            'created_at': d.created_at,
        } for d in disputes]
    except Exception:
        data = []
    return Response(data)