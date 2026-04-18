from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
import os
import mimetypes

from documents.models import Document
from cases.models import Case
from users.models import User


class UploadDocumentView(APIView):
    """Upload a document for a case"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file = request.FILES.get('file')
            doc_type = request.data.get('doc_type')
            case_id = request.data.get('case_id')
            description = request.data.get('description', '')

            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not doc_type:
                return Response({'error': 'Document type is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                return Response({'error': 'File size cannot exceed 10MB'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate file type
            allowed_types = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                return Response({'error': f'File type {file_ext} not allowed. Allowed: {", ".join(allowed_types)}'}, status=status.HTTP_400_BAD_REQUEST)

            document = Document(
                uploaded_by=request.user,
                file=file,
                doc_type=doc_type,
                description=description
            )

            # Link to case if provided
            if case_id:
                case = get_object_or_404(Case, id=case_id)
                document.case = case
                
                # Check if user has access to this case
                if request.user.role == 'client' and case.client != request.user:
                    return Response({'error': 'You do not have access to this case'}, status=status.HTTP_403_FORBIDDEN)
                if request.user.role == 'lawfirm' and case.law_firm != request.user:
                    return Response({'error': 'You do not have access to this case'}, status=status.HTTP_403_FORBIDDEN)

            document.save()

            return Response({
                'success': True,
                'message': 'Document uploaded successfully',
                'document': {
                    'id': document.id,
                    'file_name': document.file_name,
                    'file_size': document.file_size,
                    'doc_type': document.doc_type,
                    'doc_type_display': document.get_doc_type_display(),
                    'description': document.description,
                    'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_url': document.file.url
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListDocumentsView(APIView):
    """Get all documents for a case or user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        case_id = request.query_params.get('case_id')
        doc_type = request.query_params.get('doc_type')

        documents = Document.objects.all()

        # Filter by case
        if case_id:
            case = get_object_or_404(Case, id=case_id)
            # Check access
            if request.user.role == 'client' and case.client != request.user:
                return Response({'error': 'You do not have access to these documents'}, status=status.HTTP_403_FORBIDDEN)
            if request.user.role == 'lawfirm' and case.law_firm != request.user:
                return Response({'error': 'You do not have access to these documents'}, status=status.HTTP_403_FORBIDDEN)
            documents = documents.filter(case_id=case_id)

        # Filter by document type
        if doc_type:
            documents = documents.filter(doc_type=doc_type)

        # Filter by user role
        if request.user.role == 'client':
            documents = documents.filter(case__client=request.user)
        elif request.user.role == 'lawfirm':
            documents = documents.filter(case__law_firm=request.user)

        data = []
        for doc in documents:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'doc_type': doc.doc_type,
                'doc_type_display': doc.get_doc_type_display(),
                'description': doc.description,
                'uploaded_by': {
                    'id': doc.uploaded_by.id,
                    'name': doc.uploaded_by.full_name,
                    'role': doc.uploaded_by.role
                },
                'case_id': doc.case.id if doc.case else None,
                'case_title': doc.case.title if doc.case else None,
                'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_url': doc.file.url
            })

        return Response(data, status=status.HTTP_200_OK)


class DocumentDetailView(APIView):
    """Get, update, or delete a specific document"""
    permission_classes = [IsAuthenticated]

    def get_document(self, document_id, user):
        document = get_object_or_404(Document, id=document_id)
        
        # Check permissions
        if user.role == 'admin':
            return document
        if user.role == 'client' and document.case and document.case.client == user:
            return document
        if user.role == 'lawfirm' and document.case and document.case.law_firm == user:
            return document
        if document.uploaded_by == user:
            return document
        
        return None

    def get(self, request, document_id):
        document = self.get_document(document_id, request.user)
        if not document:
            return Response({'error': 'You do not have access to this document'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'id': document.id,
            'file_name': document.file_name,
            'file_size': document.file_size,
            'doc_type': document.doc_type,
            'doc_type_display': document.get_doc_type_display(),
            'description': document.description,
            'uploaded_by': {
                'id': document.uploaded_by.id,
                'name': document.uploaded_by.full_name,
                'role': document.uploaded_by.role
            },
            'case_id': document.case.id if document.case else None,
            'case_title': document.case.title if document.case else None,
            'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'file_url': document.file.url
        }, status=status.HTTP_200_OK)

    def delete(self, request, document_id):
        document = self.get_document(document_id, request.user)
        if not document:
            return Response({'error': 'You do not have access to this document'}, status=status.HTTP_403_FORBIDDEN)

        # Delete file from storage
        if document.file:
            document.file.delete(save=False)

        document.delete()
        return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)


class DownloadDocumentView(APIView):
    """Download a document file"""
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id)
        
        # Check permissions
        if request.user.role == 'admin':
            pass
        elif request.user.role == 'client' and document.case and document.case.client == request.user:
            pass
        elif request.user.role == 'lawfirm' and document.case and document.case.law_firm == request.user:
            pass
        elif document.uploaded_by == request.user:
            pass
        else:
            return Response({'error': 'You do not have permission to download this document'}, status=status.HTTP_403_FORBIDDEN)

        # Check if file exists
        if not document.file:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Open the file
            file_path = document.file.path
            if os.path.exists(file_path):
                # Determine content type
                content_type, encoding = mimetypes.guess_type(file_path)
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                # Return file response
                response = FileResponse(open(file_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
                return response
            else:
                return Response({'error': 'File not found on server'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(f"Error downloading document: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyDocumentsView(APIView):
    """Get all documents uploaded by the current user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(uploaded_by=request.user)
        
        data = []
        for doc in documents:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'doc_type': doc.doc_type,
                'doc_type_display': doc.get_doc_type_display(),
                'description': doc.description,
                'case_id': doc.case.id if doc.case else None,
                'case_title': doc.case.title if doc.case else None,
                'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_url': doc.file.url
            })
        
        return Response(data, status=status.HTTP_200_OK)


class CaseDocumentsView(APIView):
    """Get all documents for a specific case"""
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id):
        case = get_object_or_404(Case, id=case_id)
        
        # Check access
        if request.user.role == 'client' and case.client != request.user:
            return Response({'error': 'You do not have access to this case'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'lawfirm' and case.law_firm != request.user:
            return Response({'error': 'You do not have access to this case'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Document.objects.filter(case=case)
        
        data = []
        for doc in documents:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'doc_type': doc.doc_type,
                'doc_type_display': doc.get_doc_type_display(),
                'description': doc.description,
                'uploaded_by': doc.uploaded_by.full_name,
                'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_url': doc.file.url
            })
        
        return Response(data, status=status.HTTP_200_OK)