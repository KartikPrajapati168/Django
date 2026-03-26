from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from users.models import User
from profiles.models import ClientProfile,LawfirmProfile,AdminProfile
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # ✅ Profile automatically create hoga signal se

            refresh = RefreshToken.for_user(user)

            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginView(APIView):
    def post(self,request):
        email=request.data.get("email")
        password=request.data.get("password")

        user=authenticate(email=email,password=password)

        if user is None:
            return Response({"error":"Invalid credentials"},status=400)
        
        refresh=RefreshToken.for_user(user)

        #profile fetch
        profile=None

        if user.role=="client":
            profile=user.clientProfile
        elif user.role=="lawfirm":
            profile=user.lawfirmprofile
        elif user.role=="admin":
            profile=user.adminprofile
        
        return Response({
            "access":str(refresh.access_token),
            "refresh":str(refresh),
            "role":user.role,
            "is_onboarded":getattr(profile,"is_onboarded",True),
            "status":getattr(profile,"status","approved")
        })
