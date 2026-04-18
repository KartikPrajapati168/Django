from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

from profiles.models import ClientProfile, LawfirmProfile, AdminProfile
from users.models import User
from cases.models import Case
from documents.models import Document


class ClientOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            profile, created = ClientProfile.objects.get_or_create(user=user)
            
            data = request.data

            # Helper to convert empty strings to None for date fields
            def get_date_or_none(field_name):
                val = data.get(field_name)
                return val if val and val.strip() else None

            # ----- Profile fields -----
            profile.phone = data.get("phone", profile.phone)
            profile.city = data.get("city", profile.city)
            profile.date_of_birth = get_date_or_none("date_of_birth")
            profile.occupation = data.get("occupation", "")
            profile.address = data.get("address", "")
            profile.landmark = data.get("landmark", "")
            profile.pincode = data.get("pincode", "")

            # ID Proof details
            profile.id_proof_type = data.get("id_proof_type", "")
            profile.id_proof_number = data.get("id_proof_number", "")
            profile.id_proof_issue_date = get_date_or_none("id_proof_issue_date")
            profile.id_proof_expiry_date = get_date_or_none("id_proof_expiry_date")

            # ----- Create Case (map frontend field names) -----
            filing_deadline = get_date_or_none("filing_deadline")
                
            case = Case.objects.create(
                client=user,
                title=data.get("title", ""),
                description=data.get("description", ""),
                case_type=data.get("case_type", ""),
                urgency=data.get("urgency", "normal"),
                court_location=data.get("court_location", ""),
                opposing_party=data.get("opposing_party", ""),
                filing_deadline=filing_deadline,
                status="pending"
            )

            # ----- Handle ID proof document (FIX: correct field name) -----
            if request.FILES.get('id_proof_document'):
                id_doc = request.FILES['id_proof_document']
                file_path = default_storage.save(f'id_proofs/{user.id}_{id_doc.name}', ContentFile(id_doc.read()))
                profile.id_proof_document_path = file_path   # ← FIXED field name
                Document.objects.create(
                    case=case,
                    uploaded_by=user,
                    file=file_path,
                    doc_type='id_proof'
                )

            # ----- Handle case documents -----
            doc_type_mapping = {
                'documents_fir': 'fir',
                'documents_notice': 'notice',
                'documents_evidence': 'evidence',
                'documents_correspondence': 'correspondence',
                'documents_other': 'other',
            }
            for form_key, doc_type in doc_type_mapping.items():
                if request.FILES.getlist(form_key):
                    for file in request.FILES.getlist(form_key):
                        file_path = default_storage.save(f'case_docs/{user.id}_{file.name}', ContentFile(file.read()))
                        Document.objects.create(
                            case=case,
                            uploaded_by=user,
                            file=file_path,
                            doc_type=doc_type
                        )

            # ----- Consent (convert string "true"/"false" to boolean) -----
            profile.terms_accepted = data.get("terms_accepted", "false").lower() == "true"
            profile.data_consent = data.get("data_consent", "false").lower() == "true"
            profile.marketing_consent = data.get("marketing_consent", "false").lower() == "true"

            profile.is_onboarded = True
            profile.status = "pending"
            profile.save()

            return Response({
                "success": True,
                "message": "Client onboarding submitted successfully. Awaiting verification.",
                "case_id": case.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()   # This will print the real error in your console
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ========== LAW FIRM ONBOARDING ==========
class LawfirmOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            profile, created = LawfirmProfile.objects.get_or_create(user=user)
            
            # Get data from request
            data = request.data
            
            # Firm Details
            profile.firm_name = data.get("firm_name", profile.firm_name)
            profile.registration_no = data.get("registration_no", profile.registration_no)
            profile.phone = data.get("phone", profile.phone)
            profile.address = data.get("address", "")
            profile.city = data.get("city", "")
            profile.state = data.get("state", "")
            profile.website = data.get("website", "")
            
            # Firm Experience & Specialization
            profile.experience = data.get("experience", "")
            profile.specialization = data.get("specialization", "")
            
            # Primary Lawyer Details
            profile.primary_lawyer_name = data.get("primary_lawyer_name", "")
            profile.primary_lawyer_bar_council_id = data.get("primary_lawyer_bar_council_id", "")
            profile.primary_lawyer_years_experience = data.get("primary_lawyer_years_experience", None)
            profile.primary_lawyer_specialization = data.get("primary_lawyer_specialization", "")
            
            # Team Members (stored as JSON)
            team_members = data.get("team_members", "[]")
            if isinstance(team_members, str):
                team_members = json.loads(team_members)
            profile.team_members_data = json.dumps(team_members)
            
            # Terms
            profile.terms_accepted = data.get("terms_accepted", False) == 'true'
            
            # Update status
            profile.is_onboarded = True
            profile.status = "pending"
            profile.save()
            
            return Response({
                "success": True,
                "message": "Law firm onboarding submitted successfully. Awaiting verification."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in LawfirmOnboardingView: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ========== ADMIN ONBOARDING ==========
class AdminOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            profile, created = AdminProfile.objects.get_or_create(user=user)
            
            secret_key = request.data.get('secret_key')
            if secret_key != 'advocare-admin-2024':
                return Response({'error': 'Invalid secret key'}, status=400)
            
            profile.secret_key_verified = True
            profile.phone = request.data.get('phone', '')
            profile.save()
            
            # Set admin permissions
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
            return Response({
                "success": True,
                "message": "Admin profile completed successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in AdminOnboardingView: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ========== CLIENT PROFILE VIEW ==========
class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.clientprofile
            data = {
                'full_name': request.user.full_name,
                'email': request.user.email,
                'phone': profile.phone,
                'city': profile.city,
                'status': profile.status,
                'is_onboarded': profile.is_onboarded
            }
            return Response(data, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response({'error': 'Client profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== LAW FIRM PROFILE VIEW ==========
class LawfirmProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.lawfirmprofile
            data = {
                'firm_name': profile.firm_name,
                'registration_no': profile.registration_no,
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'website': profile.website,
                'experience': profile.experience,
                'specialization': profile.specialization,
                'primary_lawyer_name': profile.primary_lawyer_name,
                'primary_lawyer_bar_council_id': profile.primary_lawyer_bar_council_id,
                'primary_lawyer_years_experience': profile.primary_lawyer_years_experience,
                'primary_lawyer_specialization': profile.primary_lawyer_specialization,
                'status': profile.status,
                'is_onboarded': profile.is_onboarded
            }
            return Response(data, status=status.HTTP_200_OK)
        except LawfirmProfile.DoesNotExist:
            return Response({'error': 'Law firm profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== ADMIN PROFILE VIEW ==========
class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.adminprofile
            data = {
                'email': request.user.email,
                'full_name': request.user.full_name,
                'phone': profile.phone,
                'secret_key_verified': profile.secret_key_verified,
                'dashboard_theme': profile.dashboard_theme
            }
            return Response(data, status=status.HTTP_200_OK)
        except AdminProfile.DoesNotExist:
            return Response({'error': 'Admin profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== PENDING CLIENTS (for Admin) ==========
class PendingClientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            clients = ClientProfile.objects.filter(status="pending")
            data = []
            for c in clients:
                # Get client's latest case
                latest_case = Case.objects.filter(client=c.user).order_by('-created_at').first()
                
                data.append({
                    "id": c.id,
                    "user_id": c.user.id,
                    "name": c.user.full_name,
                    "email": c.user.email,
                    "phone": c.phone or "Not provided",
                    "city": c.city or "Not provided",
                    "id_proof_type": c.id_proof_type or "Not provided",
                    "id_proof_number": c.id_proof_number or "Not provided",
                    "case_title": latest_case.title if latest_case else "Not provided",
                    "case_type": latest_case.case_type if latest_case else "Not provided",
                    "submitted_at": c.updated_at.strftime("%Y-%m-%d %H:%M") if c.updated_at else "N/A"
                })
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in PendingClientsView: {str(e)}")
            return Response({'error': str(e)}, status=500)


# ========== PENDING LAW FIRMS (for Admin) ==========
class PendingLawFirmsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            lawfirms = LawfirmProfile.objects.filter(status="pending")
            data = []
            for lf in lawfirms:
                data.append({
                    "id": lf.id,
                    "user_id": lf.user.id,
                    "firm_name": lf.firm_name,
                    "email": lf.user.email,
                    "phone": lf.phone or "Not provided",
                    "registration_no": lf.registration_no,
                    "specialization": lf.specialization or "Not provided",
                    "experience": lf.experience or "N/A",
                    "primary_lawyer_name": lf.primary_lawyer_name or "Not provided",
                    "submitted_at": lf.updated_at.strftime("%Y-%m-%d %H:%M") if lf.updated_at else "N/A"
                })
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in PendingLawFirmsView: {str(e)}")
            return Response({'error': str(e)}, status=500)


# ========== APPROVE CLIENT ==========
class ApproveClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            profile = ClientProfile.objects.get(id=id)
            profile.status = "approved"
            profile.save()
            
            # ✅ Do NOT change case status – keep it as 'pending'
            # Case.objects.filter(client=profile.user, status='pending').update(status='assigned')  # REMOVE THIS LINE
            
            return Response({"message": "Client approved successfully"}, status=status.HTTP_200_OK)
            
        except ClientProfile.DoesNotExist:
            return Response({"error": "Client not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ========== REJECT CLIENT ==========
class RejectClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            profile = ClientProfile.objects.get(id=id)
            profile.status = "rejected"
            profile.save()
            
            # Update associated case status
            # Case.objects.filter(client=profile.user, status='pending').update(status='closed')
            
            return Response({"message": "Client rejected successfully"}, status=status.HTTP_200_OK)
            
        except ClientProfile.DoesNotExist:
            return Response({"error": "Client not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ========== APPROVE LAW FIRM ==========
class ApproveLawFirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            profile = LawfirmProfile.objects.get(id=id)
            profile.status = "approved"
            profile.is_onboarded = True
            profile.save()
            
            return Response({"message": "Law firm approved successfully"}, status=status.HTTP_200_OK)
            
        except LawfirmProfile.DoesNotExist:
            return Response({"error": "Law firm not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ========== REJECT LAW FIRM ==========
class RejectLawFirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            profile = LawfirmProfile.objects.get(id=id)
            profile.status = "rejected"
            profile.save()
            
            return Response({"message": "Law firm rejected successfully"}, status=status.HTTP_200_OK)
            
        except LawfirmProfile.DoesNotExist:
            return Response({"error": "Law firm not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ========== CLIENT DASHBOARD ==========
class ClientDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'client':
                return Response({'error': 'Client access required'}, status=403)
            
            profile = request.user.clientprofile
            
            # Get all cases for this client
            cases = Case.objects.filter(client=request.user)
            cases_data = []
            for case in cases:
                cases_data.append({
                    "id": case.id,
                    "title": case.title,
                    "case_type": case.case_type,
                    "status": case.status,
                    "urgency": case.urgency,
                    "created_at": case.created_at.strftime("%Y-%m-%d %H:%M"),
                    "court_location": case.court_location,
                    "opposing_party": case.opposing_party,
                    "law_firm_name": case.law_firm.full_name if case.law_firm else None
                })
            
            data = {
                "name": request.user.full_name,
                "email": request.user.email,
                "phone": profile.phone,
                "city": profile.city,
                "status": profile.status,
                "is_onboarded": profile.is_onboarded,
                "cases": cases_data,
                "total_cases": len(cases_data),
                "active_cases": cases.filter(status='in_progress').count(),
                "pending_cases": cases.filter(status='pending').count(),
                "closed_cases": cases.filter(status='closed').count()
            }
            return Response(data, status=status.HTTP_200_OK)
            
        except ClientProfile.DoesNotExist:
            return Response({'error': 'Client profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== LAW FIRM DASHBOARD ==========
# class LawfirmDashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             if request.user.role != 'lawfirm':
#                 return Response({'error': 'Law firm access required'}, status=403)
            
#             profile = request.user.lawfirmprofile
            
#             # Get all cases assigned to this law firm
#             assigned_cases = Case.objects.filter(law_firm=request.user)
#             cases_data = []
#             for case in assigned_cases:
#                 cases_data.append({
#                     "id": case.id,
#                     "title": case.title,
#                     "case_type": case.case_type,
#                     "status": case.status,
#                     "urgency": case.urgency,
#                     "client_name": case.client.full_name,
#                     "client_email": case.client.email,
#                     "created_at": case.created_at.strftime("%Y-%m-%d %H:%M")
#                 })
            
#             data = {
#                 "firm_name": profile.firm_name,
#                 "email": request.user.email,
#                 "phone": profile.phone,
#                 "status": profile.status,
#                 "is_onboarded": profile.is_onboarded,
#                 "registration_no": profile.registration_no,
#                 "specialization": profile.specialization,
#                 "assigned_cases": cases_data,
#                 "total_cases": len(cases_data),
#                 "active_cases": assigned_cases.filter(status='in_progress').count(),
#                 "pending_cases": assigned_cases.filter(status='assigned').count(),
#                 "closed_cases": assigned_cases.filter(status='closed').count()
#             }
#             return Response(data, status=status.HTTP_200_OK)
            
#         except LawfirmProfile.DoesNotExist:
#             return Response({'error': 'Law firm profile not found'}, status=404)
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)

class LawfirmDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'lawfirm':
                return Response({'error': 'Law firm access required'}, status=403)
            
            profile = request.user.lawfirmprofile
            
            # Get all cases assigned to this law firm
            assigned_cases = Case.objects.filter(law_firm=request.user)
            cases_data = []
            for case in assigned_cases:
                cases_data.append({
                    "id": case.id,
                    "title": case.title,
                    "case_type": case.case_type,
                    "status": case.status,
                    "urgency": case.urgency,
                    "client_name": case.client.full_name,
                    "client_email": case.client.email,
                    "created_at": case.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            data = {
                "firm_name": profile.firm_name,
                "email": request.user.email,
                "phone": profile.phone,
                "status": profile.status,
                "is_onboarded": profile.is_onboarded,
                "registration_no": profile.registration_no,
                "specialization": profile.specialization,
                "assigned_cases": cases_data,
                "total_cases": len(cases_data),
                "active_cases": assigned_cases.filter(status='in_progress').count(),
                "pending_cases": assigned_cases.filter(status='assigned').count(),
                "closed_cases": assigned_cases.filter(status='closed').count()
            }
            return Response(data, status=status.HTTP_200_OK)
            
        except LawfirmProfile.DoesNotExist:
            return Response({'error': 'Law firm profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    # ✅ ADD PUT METHOD FOR PROFILE UPDATE
    def put(self, request):
        try:
            if request.user.role != 'lawfirm':
                return Response({'error': 'Law firm access required'}, status=403)
            
            profile = request.user.lawfirmprofile
            
            # Allowed fields that can be updated
            updatable_fields = [
                'firm_name', 'registration_no', 'phone', 'website',
                'address', 'city', 'state', 'primary_lawyer_name',
                'primary_lawyer_bar_council_id', 'primary_lawyer_years_experience',
                'primary_lawyer_specialization', 'experience', 'specialization', 'bio'
            ]
            
            # Update only the fields present in request data
            for field in updatable_fields:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            
            profile.save()
            
            # Return updated profile data (same as GET response)
            assigned_cases = Case.objects.filter(law_firm=request.user)
            cases_data = []
            for case in assigned_cases:
                cases_data.append({
                    "id": case.id,
                    "title": case.title,
                    "case_type": case.case_type,
                    "status": case.status,
                    "urgency": case.urgency,
                    "client_name": case.client.full_name,
                    "client_email": case.client.email,
                    "created_at": case.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            data = {
                "firm_name": profile.firm_name,
                "email": request.user.email,
                "phone": profile.phone,
                "status": profile.status,
                "is_onboarded": profile.is_onboarded,
                "registration_no": profile.registration_no,
                "specialization": profile.specialization,
                "assigned_cases": cases_data,
                "total_cases": len(cases_data),
                "active_cases": assigned_cases.filter(status='in_progress').count(),
                "pending_cases": assigned_cases.filter(status='assigned').count(),
                "closed_cases": assigned_cases.filter(status='closed').count()
            }
            return Response(data, status=status.HTTP_200_OK)
            
        except LawfirmProfile.DoesNotExist:
            return Response({'error': 'Law firm profile not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== ADMIN DASHBOARD STATS ==========
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'admin':
                return Response({'error': 'Admin access required'}, status=403)
            
            data = {
                "totalClients": ClientProfile.objects.count(),
                "pendingClients": ClientProfile.objects.filter(status='pending').count(),
                "approvedClients": ClientProfile.objects.filter(status='approved').count(),
                "rejectedClients": ClientProfile.objects.filter(status='rejected').count(),
                "totalLawFirms": LawfirmProfile.objects.count(),
                "pendingLawFirms": LawfirmProfile.objects.filter(status='pending').count(),
                "approvedLawFirms": LawfirmProfile.objects.filter(status='approved').count(),
                "totalCases": Case.objects.count(),
                "activeCases": Case.objects.filter(status='in_progress').count(),
                "pendingCases": Case.objects.filter(status='pending').count(),
                "resolvedCases": Case.objects.filter(status='resolved').count(),
                "closedCases": Case.objects.filter(status='closed').count()
            }
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in AdminDashboardView: {str(e)}")
            return Response({'error': str(e)}, status=500)


# ========== CLIENT STATUS (FIXED) ==========
class ClientStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'client':
                return Response({'status': 'not_client', 'message': 'User is not a client'}, status=200)
            
            # Check if profile exists
            try:
                profile = request.user.clientprofile
            except ClientProfile.DoesNotExist:
                # No profile yet → user has not started onboarding
                return Response({
                    'status': 'not_submitted',
                    'name': request.user.full_name,
                    'email': request.user.email,
                }, status=status.HTTP_200_OK)
            
            # Profile exists
            # If user has not yet completed the onboarding submission (is_onboarded=False),
            # treat as not submitted (show onboarding form)
            if not profile.is_onboarded:
                return Response({
                    'status': 'not_submitted',
                    'name': request.user.full_name,
                    'email': request.user.email,
                }, status=status.HTTP_200_OK)
            
            # Otherwise return the actual status (pending, approved, rejected)
            return Response({
                'status': profile.status,
                'name': request.user.full_name,
                'email': request.user.email,
                'is_onboarded': profile.is_onboarded
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ========== LAW FIRM STATUS ==========
class LawfirmStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'lawfirm':
                return Response({'status': 'not_lawfirm', 'message': 'User is not a law firm'}, status=200)
            
            try:
                profile = request.user.lawfirmprofile
            except LawfirmProfile.DoesNotExist:
                return Response({
                    'status': 'not_submitted',
                    'firm_name': request.user.full_name,
                    'email': request.user.email,
                }, status=status.HTTP_200_OK)
            
            if not profile.is_onboarded:
                return Response({
                    'status': 'not_submitted',
                    'firm_name': profile.firm_name,
                    'email': request.user.email,
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': profile.status,
                'firm_name': profile.firm_name,
                'email': request.user.email,
                'is_onboarded': profile.is_onboarded
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        


# ========== LAW FIRMS LIST (for clients) ==========
class LawFirmsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        law_firms = User.objects.filter(role='lawfirm', lawfirmprofile__status='approved', lawfirmprofile__is_onboarded=True)
        data = []
        for firm in law_firms:
            profile = firm.lawfirmprofile
            data.append({
                'id': firm.id,
                'firm_name': profile.firm_name or firm.full_name,
                'specialization': profile.specialization or 'General',
                'city': profile.city or '',
                'state': profile.state or '',
                'experience': profile.experience or '3-5',
                'rating': profile.rating or 4.0,
                'phone': profile.phone or '',
                'email': firm.email,
            })
        # Apply filters
        spec = request.query_params.get('specialization')
        loc = request.query_params.get('location')
        min_exp = request.query_params.get('min_experience')
        if spec:
            data = [f for f in data if spec.lower() in f['specialization'].lower()]
        if loc:
            data = [f for f in data if loc.lower() in f['city'].lower() or loc.lower() in f['state'].lower()]
        if min_exp:
            data = [f for f in data if int(f['experience'].split('-')[0]) >= int(min_exp)]
        return Response(data)

# ========== AUTH ME ENDPOINT ==========
class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = None
        role = getattr(user, 'role', 'client')
        
        if role == 'client':
            profile = getattr(user, 'clientprofile', None)
        elif role == 'lawfirm':
            profile = getattr(user, 'lawfirmprofile', None)
        
        data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': role,
            'phone': profile.phone if profile else '',
            'city': profile.city if profile else '',
            'status': profile.status if profile else 'approved',
            'is_onboarded': profile.is_onboarded if profile else True,
        }
        return Response(data, status=status.HTTP_200_OK)
    


# profiles/views.py (add this class)

class ClientProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        profile = user.clientprofile

        # Update User fields
        if 'name' in request.data:
            user.full_name = request.data['name']
            user.save()

        # Update ClientProfile fields
        if 'phone' in request.data:
            profile.phone = request.data['phone']
        if 'city' in request.data:
            profile.city = request.data['city']
        profile.save()

        return Response({
            'name': user.full_name,
            'phone': profile.phone,
            'city': profile.city
        }, status=200)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ClientProfile, LawfirmProfile
from users.models import User
from cases.models import Case

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_clients(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    clients = ClientProfile.objects.select_related('user').all()
    data = []
    for cp in clients:
        data.append({
            'id': cp.id,
            'name': cp.user.full_name,
            'email': cp.user.email,
            'phone': cp.phone,
            'id_proof_type': cp.id_proof_type,
            'id_proof_number': cp.id_proof_number,
            'status': cp.status,
            'case_title': getattr(cp, 'case_title', 'N/A'),
            'case_type': getattr(cp, 'case_type', 'N/A'),
            'case_description': getattr(cp, 'case_description', ''),
            'submitted_at': cp.created_at,
            'address': cp.address,
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_lawfirms(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    firms = LawfirmProfile.objects.select_related('user').all()
    data = []
    for lp in firms:
        data.append({
            'id': lp.id,
            'firm_name': lp.firm_name,
            'email': lp.user.email,
            'phone': lp.phone,
            'registration_no': lp.registration_no,
            'specialization': lp.specialization,
            'primary_lawyer_name': lp.primary_lawyer_name,
            'status': lp.status,
            'submitted_at': lp.created_at,
            'address': lp.address,
            'city': lp.city,
            'state': lp.state,
            'gst_no': getattr(lp, 'gst_no', ''),
            'total_cases': Case.objects.filter(law_firm=lp.user).count(),
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_analytics(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    # You can replace with real analytics later
    data = {
        'totalLogins': '248',
        'apiRequests': '5,120',
        'avgCaseDuration': '42 days',
        'avgResolution': '28 days',
        'logs': [
            {'action': 'Client Approved', 'user': 'Admin', 'target': 'Rajesh Kumar', 'time': '2 min ago', 'type': 'success'},
            {'action': 'Law Firm Approved', 'user': 'Admin', 'target': 'Mehta & Associates', 'time': '15 min ago', 'type': 'success'},
            {'action': 'Case Assigned', 'user': 'System', 'target': 'Case #142 → Mehta & Assoc.', 'time': '1 hr ago', 'type': 'info'},
            {'action': 'Court Update Sent', 'user': 'Admin', 'target': 'Case #138 - Hearing on 25 Apr', 'time': '2 hrs ago', 'type': 'info'},
            {'action': 'Client Rejected', 'user': 'Admin', 'target': 'Priya Patel - Incomplete docs', 'time': '3 hrs ago', 'type': 'error'},
        ]
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    stats = {
        'totalClients': ClientProfile.objects.count(),
        'totalLawFirms': LawfirmProfile.objects.count(),
        'pendingClients': ClientProfile.objects.filter(status='pending').count(),
        'pendingLawFirms': LawfirmProfile.objects.filter(status='pending').count(),
        'activeCases': Case.objects.filter(status='in_progress').count(),
        'approvedClients': ClientProfile.objects.filter(status='approved').count(),
    }
    return Response(stats)



































# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from profiles.models import ClientProfile, LawfirmProfile, AdminProfile
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# import os
# import json

# # ========== CLIENT ONBOARDING ==========
# class ClientOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         try:
#             profile = user.clientprofile
#         except ClientProfile.DoesNotExist:
#             return Response({'error': 'Client profile not found'}, status=404)

#         # Get data from request
#         data = request.data
        
#         # Update profile fields
#         profile.phone = data.get("phone", profile.phone)
#         profile.city = data.get("city", profile.city)
#         profile.date_of_birth = data.get("date_of_birth", None)
#         profile.occupation = data.get("occupation", "")
#         profile.address = data.get("address", "")
#         profile.landmark = data.get("landmark", "")
#         profile.pincode = data.get("pincode", "")
        
#         # ID Proof details
#         profile.id_proof_type = data.get("id_proof_type", "")
#         profile.id_proof_number = data.get("id_proof_number", "")
#         profile.id_proof_issue_date = data.get("id_proof_issue_date", None)
#         profile.id_proof_expiry_date = data.get("id_proof_expiry_date", None)
        
#         # Case details
#         profile.case_title = data.get("case_title", "")
#         profile.case_description = data.get("case_description", "")
#         profile.case_type = data.get("case_type", "")
#         profile.case_urgency = data.get("case_urgency", "normal")
#         profile.court_location = data.get("court_location", "")
#         profile.opposing_party = data.get("opposing_party", "")
#         profile.filing_deadline = data.get("filing_deadline", None)
        
#         # Handle ID proof document upload
#         if request.FILES.get('id_proof_document'):
#             id_doc = request.FILES['id_proof_document']
#             file_path = default_storage.save(f'id_proofs/{user.id}_{id_doc.name}', ContentFile(id_doc.read()))
#             profile.id_proof_document = file_path
        
#         # Handle case documents upload
#         documents_data = {}
#         for key in ['documents_fir', 'documents_notice', 'documents_evidence', 
#                     'documents_correspondence', 'documents_other']:
#             if request.FILES.getlist(key):
#                 file_paths = []
#                 for file in request.FILES.getlist(key):
#                     file_path = default_storage.save(f'case_docs/{user.id}_{file.name}', ContentFile(file.read()))
#                     file_paths.append(file_path)
#                 documents_data[key] = file_paths
        
#         profile.documents = json.dumps(documents_data) if documents_data else "{}"
        
#         # Terms and consent
#         profile.terms_accepted = data.get("terms_accepted", False) == 'true'
#         profile.data_consent = data.get("data_consent", False) == 'true'
#         profile.marketing_consent = data.get("marketing_consent", False) == 'true'
        
#         # Update status
#         profile.is_onboarded = True
#         profile.status = "pending"
        
#         profile.save()
        
#         return Response({
#             "success": True,
#             "message": "Client onboarding submitted successfully. Awaiting verification."
#         }, status=status.HTTP_200_OK)


# # ========== CLIENT PROFILE VIEW ==========
# class ClientProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         try:
#             profile = user.clientprofile
#         except ClientProfile.DoesNotExist:
#             return Response({'error': 'Client profile not found'}, status=404)

#         data = {
#             'full_name': user.get_full_name() or user.username,
#             'email': user.email,
#             'phone': profile.phone,
#             'city': profile.city,
#         }
#         return Response(data)


# # ========== LAW FIRM ONBOARDING ==========
# class LawfirmOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         try:
#             profile = user.lawfirmprofile
#         except LawfirmProfile.DoesNotExist:
#             return Response({'error': 'Law firm profile not found'}, status=404)

#         profile.firm_name = request.data.get("firm_name", profile.firm_name)
#         profile.registration_no = request.data.get("registration_no", profile.registration_no)
#         profile.phone = request.data.get("phone", profile.phone)
#         profile.address = request.data.get("address", "")
#         profile.specialization = request.data.get("specialization", "")
#         profile.years_of_experience = request.data.get("years_of_experience", 0)
#         profile.description = request.data.get("description", "")

#         profile.is_onboarded = True
#         profile.status = "pending"
#         profile.save()

#         return Response({"message": "Law firm onboarding submitted successfully"}, status=status.HTTP_200_OK)


# # ========== ADMIN ONBOARDING ==========
# class AdminOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         try:
#             profile = user.adminprofile
#         except AdminProfile.DoesNotExist:
#             return Response({'error': 'Admin profile not found'}, status=404)
            
#         secret_key = request.data.get('secret_key')
#         if secret_key != 'advocare-admin-2024':
#             return Response({'error': 'Invalid secret key'}, status=400)
            
#         profile.secret_key_verified = True
#         profile.phone = request.data.get('phone', '')
#         profile.save()
        
#         return Response({'message': 'Admin profile completed'}, status=status.HTTP_200_OK)


# # ========== PENDING CLIENTS (for Admin) ==========
# class PendingClientsView(APIView):
#     permission_classes = [IsAuthenticated]  # Change from IsAdminUser

#     def get(self, request):
#         # Manual admin check
#         if request.user.role != 'admin':
#             return Response({'error': 'Admin access required'}, status=403)
        
#         clients = ClientProfile.objects.filter(status="pending")
#         data = []
#         for c in clients:
#             data.append({
#                 "id": c.id,
#                 "name": c.user.full_name,
#                 "email": c.user.email,
#                 "phone": c.phone,
#                 "id_proof_type": c.id_proof_type,
#                 "id_proof_number": c.id_proof_number,
#                 "case_title": c.case_title,
#                 "case_type": c.case_type,
#                 "submitted_at": c.updated_at.strftime("%Y-%m-%d %H:%M") if hasattr(c, 'updated_at') else "N/A"
#             })
#         return Response(data, status=status.HTTP_200_OK)


# # ========== APPROVE CLIENT ==========
# class ApproveClientView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, id):
#         if request.user.role != 'admin':
#             return Response({'error': 'Admin access required'}, status=403)
            
#         try:
#             profile = ClientProfile.objects.get(id=id)
#             profile.status = "approved"
#             profile.save()
#             return Response({"message": "Client approved successfully"}, status=status.HTTP_200_OK)
#         except ClientProfile.DoesNotExist:
#             return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)


# # ========== REJECT CLIENT ==========
# class RejectClientView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, id):
#         if request.user.role != 'admin':
#             return Response({'error': 'Admin access required'}, status=403)
            
#         try:
#             profile = ClientProfile.objects.get(id=id)
#             profile.status = "rejected"
#             profile.save()
#             return Response({"message": "Client rejected successfully"}, status=status.HTTP_200_OK)
#         except ClientProfile.DoesNotExist:
#             return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)


# # ========== CLIENT DASHBOARD ==========
# from profiles.permissions import IsApprovedUser

# class ClientDashboardView(APIView):
#     permission_classes = [IsAuthenticated, IsApprovedUser]

#     def get(self, request):
#         user = request.user
#         try:
#             profile = user.clientprofile
#         except ClientProfile.DoesNotExist:
#             return Response({'error': 'Client profile not found'}, status=404)

#         data = {
#             "name": user.get_full_name() or user.username,
#             "email": user.email,
#             "phone": profile.phone,
#             "city": profile.city,
#             "status": profile.status,
#             "case_title": profile.case_title,
#             "case_type": profile.case_type,
#             "case_status": profile.status
#         }
#         return Response(data, status=status.HTTP_200_OK)


# # ========== LAW FIRM DASHBOARD ==========
# class LawfirmDashboardView(APIView):
#     permission_classes = [IsAuthenticated, IsApprovedUser]

#     def get(self, request):
#         user = request.user
#         try:
#             profile = user.lawfirmprofile
#         except LawfirmProfile.DoesNotExist:
#             return Response({'error': 'Law firm profile not found'}, status=404)

#         data = {
#             "firm_name": profile.firm_name,
#             "email": user.email,
#             "phone": profile.phone,
#             "status": profile.status
#         }
#         return Response(data, status=status.HTTP_200_OK)


# # ========== ADMIN DASHBOARD STATS ==========
# class AdminDashboardView(APIView):
#     permission_classes = [IsAuthenticated]  # Change from IsAdminUser

#     def get(self, request):
#         # Manual admin check
#         if request.user.role != 'admin':
#             return Response({'error': 'Admin access required'}, status=403)
            
#         total_clients = ClientProfile.objects.count()
#         pending_clients = ClientProfile.objects.filter(status="pending").count()
#         approved_clients = ClientProfile.objects.filter(status="approved").count()
        
#         data = {
#             "totalClients": total_clients,
#             "pendingOnboarding": pending_clients,
#             "approvedClients": approved_clients,
#             "activeCases": 0,
#         }
#         return Response(data, status=status.HTTP_200_OK)





# # Add this class at the end of your profiles/views.py

# class ClientStatusView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         try:
#             profile = user.clientprofile
#             status = profile.status if hasattr(profile, 'status') else 'not_onboarded'
#         except ClientProfile.DoesNotExist:
#             status = 'no_profile'
        
#         return Response({
#             'status': status,
#             'name': user.full_name,
#             'email': user.email,
#         }, status=status.HTTP_200_OK)



















# from django.shortcuts import render

# # Create your views here.
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from profiles.models import ClientProfile,LawfirmProfile,AdminProfile

# class ClientOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         profile = user.clientprofile

#         profile.phone = request.data.get("phone",profile.phone)
#         profile.city = request.data.get("city",profile.city)

#         profile.is_onboarded = True
#         profile.status = "pending"

#         profile.save()

#         return Response({"message": "Client onboarding submitted"})
    

# # profiles/views.py (add this at the end)

# class ClientProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         try:
#             profile = user.clientprofile
#         except ClientProfile.DoesNotExist:
#             return Response({'error': 'Client profile not found'}, status=404)

#         data = {
#             'full_name': user.full_name,
#             'email': user.email,
#             'phone': profile.phone,
#             'city': profile.city,
#         }
#         return Response(data)

# class LawfirmOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self,request):
#         user=request.user
#         profile=user.lawfirmprofile

#         profile.firm_name=request.data.get("firm_name")
#         profile.registration_no=request.data.get("registration_no")

#         profile.is_onboarded=True
#         profile.status="pending"

#         profile.save()

#         return Response({"message":"Lawfirm onboarding submitted"})
    

# class PendingClientsView(APIView):
#     def get(self, request):
#         clients = ClientProfile.objects.filter(status="pending")
#         data = [
#             {
#                 "id": c.id,
#                 "name": c.user.full_name,
#                 "email": c.user.email
#             }
#             for c in clients
#         ]
#         return Response(data)
    

# class ApproveClientView(APIView):
#     def post(self, request, id):
#         profile = ClientProfile.objects.get(id=id)
#         profile.status = "approved"
#         profile.save()

#         return Response({"message": "Client approved"})
    

# class RejectClientView(APIView):
#     def post(self, request, id):
#         profile = ClientProfile.objects.get(id=id)
#         profile.status = "rejected"
#         profile.save()

#         return Response({"message": "Client rejected"})
    

# from rest_framework.permissions import IsAuthenticated
# from profiles.permissions import IsApprovedUser

# class ClientDashboardView(APIView):
#     permission_classes = [IsAuthenticated, IsApprovedUser]

#     def get(self, request):
#         user = request.user
#         profile = user.clientprofile

#         data = {
#             "name": user.full_name,
#             "email": user.email,
#             "phone": profile.phone,
#             "city": profile.city,
#             "status": profile.status
#         }

#         return Response(data)
    
# class LawfirmDashboardView(APIView):
#     permission_classes = [IsAuthenticated, IsApprovedUser]

#     def get(self, request):
#         user = request.user
#         profile = user.lawfirmprofile

#         data = {
#             "firm_name": profile.firm_name,
#             "email": user.email,
#             "phone": profile.phone,
#             "status": profile.status
#         }

#         return Response(data)
    

# class AdminOnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         profile = user.adminprofile
#         secret_key = request.data.get('secret_key')
#         # Check against a fixed secret (you can also store in a model)
#         if secret_key != 'advocare-admin-2024':   # change to your actual secret
#             return Response({'error': 'Invalid secret key'}, status=400)
#         profile.secret_key_verified = True
#         profile.phone = request.data.get('phone', '')
#         profile.save()
#         return Response({'message': 'Admin profile completed'})
    
