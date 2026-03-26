from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from profiles.models import ClientProfile,LawfirmProfile,AdminProfile

class ClientOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = user.clientprofile

        profile.phone = request.data.get("phone")
        profile.city = request.data.get("city")

        profile.is_onboarded = True
        profile.status = "pending"

        profile.save()

        return Response({"message": "Client onboarding submitted"})
    

class LawfirmOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user=request.user
        profile=user.lawfirmprofile

        profile.firm_name=request.data.get("firm_name")
        profile.registration_no=request.data.get("registration_no")

        profile.is_onboarded=True
        profile.status="pending"

        profile.save()

        return Response({"message":"Lawfirm onboarding submitted"})
    

class PendingClientsView(APIView):
    def get(self, request):
        clients = ClientProfile.objects.filter(status="pending")
        data = [
            {
                "id": c.id,
                "name": c.user.full_name,
                "email": c.user.email
            }
            for c in clients
        ]
        return Response(data)
    

class ApproveClientView(APIView):
    def post(self, request, id):
        profile = ClientProfile.objects.get(id=id)
        profile.status = "approved"
        profile.save()

        return Response({"message": "Client approved"})
    

class RejectClientView(APIView):
    def post(self, request, id):
        profile = ClientProfile.objects.get(id=id)
        profile.status = "rejected"
        profile.save()

        return Response({"message": "Client rejected"})
    

from rest_framework.permissions import IsAuthenticated
from profiles.permissions import IsApprovedUser

class ClientDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def get(self, request):
        user = request.user
        profile = user.clientprofile

        data = {
            "name": user.full_name,
            "email": user.email,
            "phone": profile.phone,
            "city": profile.city,
            "status": profile.status
        }

        return Response(data)
    
class LawfirmDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def get(self, request):
        user = request.user
        profile = user.lawfirmprofile

        data = {
            "firm_name": profile.firm_name,
            "email": user.email,
            "phone": profile.phone,
            "status": profile.status
        }

        return Response(data)