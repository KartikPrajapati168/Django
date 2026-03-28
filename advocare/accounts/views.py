# accounts/views.py

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from users.models import User
from profiles.models import ClientProfile, LawfirmProfile, AdminProfile


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        role = data.get('role')           # 'client', 'lawfirm', 'admin'
        phone = data.get('phone', '')
        city = data.get('city', '')
        # lawfirm specific
        firm_name = data.get('firm_name')
        registration_no = data.get('registration_no')
        experience = data.get('experience')
        specialization = data.get('specialization')
        # admin specific
        secret_key = data.get('secret_key')

        # Validation
        if not email or not password or not full_name or not role:
            return Response({'error': 'Missing required fields'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=400)

        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
        )

        # Create role-specific profile
        if role == 'client':
            ClientProfile.objects.create(
                user=user,
                phone=phone,
                city=city,
            )
        elif role == 'lawfirm':
            if not firm_name or not registration_no:
                return Response({'error': 'Firm name and registration number required'}, status=400)
            LawfirmProfile.objects.create(
                user=user,
                firm_name=firm_name,
                registration_no=registration_no,
                phone=phone,
                experience=experience,
                specialization=specialization,
            )
        elif role == 'admin':
            if not secret_key:
                return Response({'error': 'Secret key required for admin'}, status=400)
            # Create admin profile and store hashed secret key
            admin_profile = AdminProfile.objects.create(
                user=user,
                phone=phone,
                secret_key_verified=True,   # will be set true after hashing
            )
            admin_profile.set_secret_key(secret_key)   # hashes and saves
        else:
            return Response({'error': 'Invalid role'}, status=400)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role,
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')
        registration_no = request.data.get('registration_no')   # lawfirm
        secret_key = request.data.get('secret_key')             # admin

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)

        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=400)

        # Role validation
        if role and user.role != role:
            return Response({'error': f'User is not a {role}'}, status=400)

        # Law firm: verify registration number
        if user.role == 'lawfirm':
            if not hasattr(user, 'lawfirmprofile'):
                return Response({'error': 'Law firm profile not found'}, status=400)
            if registration_no and user.lawfirmprofile.registration_no != registration_no:
                return Response({'error': 'Invalid registration number'}, status=400)

        # Admin: verify secret key using stored hash
        elif user.role == 'admin':
            if not hasattr(user, 'adminprofile'):
                return Response({'error': 'Admin profile not found'}, status=400)
            if not secret_key:
                return Response({'error': 'Secret key required for admin login'}, status=400)
            if not user.adminprofile.check_secret_key(secret_key):
                return Response({'error': 'Invalid admin secret key'}, status=400)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Optional: return profile info (is_onboarded, status)
        profile = None
        if user.role == 'client':
            profile = user.clientprofile
        elif user.role == 'lawfirm':
            profile = user.lawfirmprofile
        elif user.role == 'admin':
            profile = user.adminprofile

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role,
            'is_onboarded': getattr(profile, 'is_onboarded', True),
            'status': getattr(profile, 'status', 'approved'),
        })