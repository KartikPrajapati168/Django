import os
import mimetypes
import tempfile
import traceback

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import FileResponse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from documents.models import Document
from cases.models import Case
from users.models import User

from .utils.document_verifier import verify_document


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

class UploadDocumentView(APIView):
    """Upload a document for a case"""

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            file = request.FILES.get("file")
            doc_type = request.data.get("doc_type")
            case_id = request.data.get("case_id")

            # ------------------------------------------------
            # Validate file
            # ------------------------------------------------

            if not file:

                return Response(
                    {
                        "error": "No file provided"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not doc_type:

                return Response(
                    {
                        "error":
                            "Document type is required"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # File size
            # ------------------------------------------------

            if file.size > 10 * 1024 * 1024:

                return Response(
                    {
                        "error":
                            "File size cannot exceed 10MB"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # File extension
            # ------------------------------------------------

            allowed_types = [
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "doc",
                "docx",
            ]

            file_ext = (
                file.name
                .split(".")[-1]
                .lower()
            )

            if file_ext not in allowed_types:

                return Response(
                    {
                        "error":
                            f"File type {file_ext} not allowed. "
                            f"Allowed: {', '.join(allowed_types)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Create document
            # ------------------------------------------------

            document = Document(
                uploaded_by=request.user,
                file=file,
                doc_type=doc_type,
            )

            # ------------------------------------------------
            # Link case
            # ------------------------------------------------

            if case_id:

                case = get_object_or_404(
                    Case,
                    id=case_id
                )

                # Client access
                if (
                    request.user.role == "client"
                    and case.client != request.user
                ):

                    return Response(
                        {
                            "error":
                                "You do not have access to this case"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Law firm access
                if (
                    request.user.role == "lawfirm"
                    and case.law_firm != request.user
                ):

                    return Response(
                        {
                            "error":
                                "You do not have access to this case"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                document.case = case

            # ------------------------------------------------
            # Save
            # ------------------------------------------------

            document.save()

            return Response(
                {
                    "success": True,
                    "message":
                        "Document uploaded successfully",

                    "document": {
                        "id": document.id,
                        "file_name": document.file_name,
                        "file_size": document.file_size,
                        "doc_type": document.doc_type,
                        "doc_type_display":
                            document.get_doc_type_display(),
                        "uploaded_at":
                            document.uploaded_at.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        "file_url":
                            document.file.url,
                    },
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            print(
                "UPLOAD DOCUMENT ERROR:",
                repr(e)
            )

            traceback.print_exc()

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# LIST DOCUMENTS
# ============================================================

class ListDocumentsView(APIView):
    """Get all documents for a case or user"""

    permission_classes = [IsAuthenticated]

    def get(self, request):

        case_id = request.query_params.get(
            "case_id"
        )

        doc_type = request.query_params.get(
            "doc_type"
        )

        documents = Document.objects.all()

        # ------------------------------------------------
        # Case filter
        # ------------------------------------------------

        if case_id:

            case = get_object_or_404(
                Case,
                id=case_id
            )

            if (
                request.user.role == "client"
                and case.client != request.user
            ):

                return Response(
                    {
                        "error":
                            "You do not have access to these documents"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            if (
                request.user.role == "lawfirm"
                and case.law_firm != request.user
            ):

                return Response(
                    {
                        "error":
                            "You do not have access to these documents"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            documents = documents.filter(
                case_id=case_id
            )

        # ------------------------------------------------
        # Document type
        # ------------------------------------------------

        if doc_type:

            documents = documents.filter(
                doc_type=doc_type
            )

        # ------------------------------------------------
        # User role
        # ------------------------------------------------

        if request.user.role == "client":

            documents = documents.filter(
                case__client=request.user
            )

        elif request.user.role == "lawfirm":

            documents = documents.filter(
                case__law_firm=request.user
            )

        # ------------------------------------------------
        # Response
        # ------------------------------------------------

        data = []

        for doc in documents:

            data.append(
                {
                    "id": doc.id,
                    "file_name": doc.file_name,
                    "file_size": doc.file_size,
                    "doc_type": doc.doc_type,
                    "doc_type_display":
                        doc.get_doc_type_display(),

                    "uploaded_by": {
                        "id":
                            doc.uploaded_by.id,

                        "name":
                            doc.uploaded_by.full_name,

                        "role":
                            doc.uploaded_by.role,
                    },

                    "case_id":
                        doc.case.id
                        if doc.case
                        else None,

                    "case_title":
                        doc.case.title
                        if doc.case
                        else None,

                    "uploaded_at":
                        doc.uploaded_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "file_url":
                        doc.file.url,
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )


# ============================================================
# DOCUMENT DETAIL
# ============================================================

class DocumentDetailView(APIView):
    """Get or delete a specific document"""

    permission_classes = [IsAuthenticated]

    def get_document(
        self,
        document_id,
        user
    ):

        document = get_object_or_404(
            Document,
            id=document_id
        )

        # Admin
        if user.role == "admin":
            return document

        # Client
        if (
            user.role == "client"
            and document.case
            and document.case.client == user
        ):
            return document

        # Law firm
        if (
            user.role == "lawfirm"
            and document.case
            and document.case.law_firm == user
        ):
            return document

        # Owner
        if document.uploaded_by == user:
            return document

        return None

    def get(
        self,
        request,
        document_id
    ):

        document = self.get_document(
            document_id,
            request.user
        )

        if not document:

            return Response(
                {
                    "error":
                        "You do not have access to this document"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "id": document.id,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "doc_type": document.doc_type,
                "doc_type_display":
                    document.get_doc_type_display(),

                "uploaded_by": {
                    "id":
                        document.uploaded_by.id,

                    "name":
                        document.uploaded_by.full_name,

                    "role":
                        document.uploaded_by.role,
                },

                "case_id":
                    document.case.id
                    if document.case
                    else None,

                "case_title":
                    document.case.title
                    if document.case
                    else None,

                "uploaded_at":
                    document.uploaded_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "file_url":
                    document.file.url,
            },
            status=status.HTTP_200_OK
        )

    def delete(
        self,
        request,
        document_id
    ):

        document = self.get_document(
            document_id,
            request.user
        )

        if not document:

            return Response(
                {
                    "error":
                        "You do not have access to this document"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if document.file:

            document.file.delete(
                save=False
            )

        document.delete()

        return Response(
            {
                "message":
                    "Document deleted successfully"
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# DOWNLOAD DOCUMENT
# ============================================================

class DownloadDocumentView(APIView):
    """Download a document file"""

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        document_id
    ):

        document = get_object_or_404(
            Document,
            id=document_id
        )

        # ------------------------------------------------
        # Permission
        # ------------------------------------------------

        allowed = False

        if request.user.role == "admin":

            allowed = True

        elif (
            request.user.role == "client"
            and document.case
            and document.case.client == request.user
        ):

            allowed = True

        elif (
            request.user.role == "lawfirm"
            and document.case
            and document.case.law_firm == request.user
        ):

            allowed = True

        elif document.uploaded_by == request.user:

            allowed = True

        if not allowed:

            return Response(
                {
                    "error":
                        "You do not have permission to download this document"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ------------------------------------------------
        # File check
        # ------------------------------------------------

        if not document.file:

            return Response(
                {
                    "error": "File not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            file_path = document.file.path

            if not os.path.exists(file_path):

                return Response(
                    {
                        "error":
                            "File not found on server"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            content_type, encoding = (
                mimetypes.guess_type(file_path)
            )

            if content_type is None:

                content_type = (
                    "application/octet-stream"
                )

            response = FileResponse(
                open(file_path, "rb"),
                content_type=content_type
            )

            response[
                "Content-Disposition"
            ] = (
                f'attachment; '
                f'filename="{document.file_name}"'
            )

            return response

        except Exception as e:

            print(
                "DOWNLOAD DOCUMENT ERROR:",
                repr(e)
            )

            traceback.print_exc()

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# MY DOCUMENTS
# ============================================================

class MyDocumentsView(APIView):
    """Get all documents uploaded by current user"""

    permission_classes = [IsAuthenticated]

    def get(self, request):

        documents = Document.objects.filter(
            uploaded_by=request.user
        )

        data = []

        for doc in documents:

            data.append(
                {
                    "id": doc.id,
                    "file_name": doc.file_name,
                    "file_size": doc.file_size,
                    "doc_type": doc.doc_type,
                    "doc_type_display":
                        doc.get_doc_type_display(),

                    "case_id":
                        doc.case.id
                        if doc.case
                        else None,

                    "case_title":
                        doc.case.title
                        if doc.case
                        else None,

                    "uploaded_at":
                        doc.uploaded_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "file_url":
                        doc.file.url,
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )


# ============================================================
# CASE DOCUMENTS
# ============================================================

class CaseDocumentsView(APIView):
    """Get all documents for a specific case"""

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        case_id
    ):

        case = get_object_or_404(
            Case,
            id=case_id
        )

        # ------------------------------------------------
        # Access check
        # ------------------------------------------------

        if (
            request.user.role == "client"
            and case.client != request.user
        ):

            return Response(
                {
                    "error":
                        "You do not have access to this case"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if (
            request.user.role == "lawfirm"
            and case.law_firm != request.user
        ):

            return Response(
                {
                    "error":
                        "You do not have access to this case"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        documents = Document.objects.filter(
            case=case
        )

        data = []

        for doc in documents:

            data.append(
                {
                    "id": doc.id,
                    "file_name": doc.file_name,
                    "file_size": doc.file_size,
                    "doc_type": doc.doc_type,
                    "doc_type_display":
                        doc.get_doc_type_display(),

                    "uploaded_by":
                        doc.uploaded_by.full_name,

                    "uploaded_at":
                        doc.uploaded_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "file_url":
                        doc.file.url,
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )


# ============================================================
# DOCUMENT VERIFICATION / OCR
# ============================================================

class DocumentVerifyView(APIView):
    """
    Verify uploaded document using OCR.
    Supports PDF, JPG, JPEG and PNG.
    """

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        print("")
        print("==========================================")
        print("DOCUMENT VERIFY REQUEST")
        print("==========================================")

        # ------------------------------------------------
        # Get uploaded file
        # ------------------------------------------------

        file_obj = request.FILES.get(
            "document"
        )

        expected_type = request.data.get(
            "expected_type"
        )

        print(
            "User:",
            request.user
        )

        print(
            "File:",
            getattr(
                file_obj,
                "name",
                None
            )
        )

        print(
            "Expected type:",
            expected_type
        )

        # ------------------------------------------------
        # Required file
        # ------------------------------------------------

        if not file_obj:

            return Response(
                {
                    "valid": False,
                    "message":
                        "Document file is required.",
                    "extracted": {},
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ------------------------------------------------
        # Required document type
        # ------------------------------------------------

        if not expected_type:

            return Response(
                {
                    "valid": False,
                    "message":
                        "Expected document type is required.",
                    "extracted": {},
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ------------------------------------------------
        # Extra data
        # ------------------------------------------------

        extra_data = {
            "expected_name":
                request.data.get(
                    "expected_name"
                ),

            "expected_address":
                request.data.get(
                    "expected_address"
                ),

            "expected_phone":
                request.data.get(
                    "expected_phone"
                ),

            "expected_firm_name":
                request.data.get(
                    "expected_firm_name"
                ),

            "expected_registration_no":
                request.data.get(
                    "expected_registration_no"
                ),
        }

        extra_data = {
            key: value
            for key, value
            in extra_data.items()
            if value not in (
                None,
                ""
            )
        }

        print(
            "Verification data:",
            extra_data
        )

        # ------------------------------------------------
        # Extension
        # ------------------------------------------------

        original_name = (
            getattr(
                file_obj,
                "name",
                "document"
            )
            or "document"
        )

        extension = os.path.splitext(
            original_name
        )[1].lower()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
            ".webp",
            ".bmp",
            ".tiff",
            ".tif",
        }

        if extension not in allowed_extensions:

            return Response(
                {
                    "valid": False,
                    "message":
                        "Unsupported file type. "
                        "Use PDF, JPG, JPEG or PNG.",
                    "extracted": {},
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ------------------------------------------------
        # File size
        # ------------------------------------------------

        if file_obj.size > 10 * 1024 * 1024:

            return Response(
                {
                    "valid": False,
                    "message":
                        "File size cannot exceed 10MB.",
                    "extracted": {},
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tmp_path = None

        try:

            # ------------------------------------------------
            # Create temporary file
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension
            ) as tmp_file:

                for chunk in file_obj.chunks():

                    tmp_file.write(
                        chunk
                    )

                tmp_path = tmp_file.name

            print(
                "Temporary file:",
                tmp_path
            )

            print(
                "Temporary file size:",
                os.path.getsize(
                    tmp_path
                )
            )

            # ------------------------------------------------
            # VERIFY DOCUMENT
            # ------------------------------------------------

            result = verify_document(
                tmp_path,
                expected_type,
                **extra_data
            )

            print(
                "Verification result:",
                result
            )

            # ------------------------------------------------
            # Make sure result is a dictionary
            # ------------------------------------------------

            if not isinstance(
                result,
                dict
            ):

                print(
                    "ERROR: verify_document returned:",
                    type(result)
                )

                return Response(
                    {
                        "valid": False,
                        "message":
                            "Document verification returned an invalid response.",
                        "extracted": {},
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                result,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            print("")
            print(
                "=========================================="
            )

            print(
                "DOCUMENT VERIFY ERROR"
            )

            print(
                "Exception type:",
                type(e).__name__
            )

            print(
                "Exception:",
                str(e)
            )

            print(
                "=========================================="
            )

            traceback.print_exc()

            return Response(
                {
                    "valid": False,
                    "message":
                        "Document processing failed.",
                    "error_type":
                        type(e).__name__,
                    "error":
                        str(e),
                    "extracted": {},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:

            # ------------------------------------------------
            # Delete temporary file
            # ------------------------------------------------

            if (
                tmp_path
                and
                os.path.exists(tmp_path)
            ):

                try:

                    os.unlink(
                        tmp_path
                    )

                    print(
                        "Temporary file deleted."
                    )

                except Exception as e:

                    print(
                        "Temporary file cleanup failed:",
                        repr(e)
                    )
















# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
# import os
# import tempfile

# from .utils.ocr_nlp import verify_document

# class DocumentVerifyView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request, *args, **kwargs):
#         file_obj = request.data.get('document')
#         expected_type = request.data.get('expected_type')  # fir, notice, aadhar, pan, etc.
        
#         if not file_obj or not expected_type:
#             return Response({"error": "Both 'document' and 'expected_type' are required."}, status=400)
        
#         # Save file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_obj.name)[1]) as tmp_file:
#             for chunk in file_obj.chunks():
#                 tmp_file.write(chunk)
#             tmp_path = tmp_file.name
        
#         try:
#             result = verify_document(tmp_path, expected_type)
#             return Response(result)
#         finally:
#             os.unlink(tmp_path)





