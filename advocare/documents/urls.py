from django.urls import path
from .views import (
    UploadDocumentView,
    ListDocumentsView,
    DocumentDetailView,
    DownloadDocumentView,
    MyDocumentsView,
    CaseDocumentsView
)

urlpatterns = [
    # Upload and list
    path('upload/', UploadDocumentView.as_view(), name='upload-document'),
    path('list/', ListDocumentsView.as_view(), name='list-documents'),
    path('my-documents/', MyDocumentsView.as_view(), name='my-documents'),
    
    # Specific document operations
    path('<int:document_id>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<int:document_id>/download/', DownloadDocumentView.as_view(), name='download-document'),
    
    # Case-specific documents
    path('case/<int:case_id>/', CaseDocumentsView.as_view(), name='case-documents'),
]