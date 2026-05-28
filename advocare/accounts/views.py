from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.models import User
from profiles.models import ClientProfile, LawfirmProfile, AdminProfile

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        role = data.get('role')
        phone = data.get('phone', '')
        city = data.get('city', '')
        firm_name = data.get('firm_name')
        registration_no = data.get('registration_no')
        experience = data.get('experience')
        specialization = data.get('specialization')
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
                is_onboarded=False,
                status='not_submitted'
            )
        elif role == 'admin':
            if not secret_key:
                return Response({'error': 'Secret key required for admin'}, status=400)
            
            # Create admin profile
            admin_profile = AdminProfile.objects.create(
                user=user,
                phone=phone,
                secret_key_verified=True,
            )
            admin_profile.set_secret_key(secret_key)
            
            # ✅ CRITICAL FIX: Set admin permissions automatically
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
        else:
            return Response({'error': 'Invalid role'}, status=400)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
            }
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')
        registration_no = request.data.get('registration_no')
        secret_key = request.data.get('secret_key')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)

        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=400)

        # Check if user is active
        if not user.is_active:
            return Response({'error': 'Account is deactivated. Contact admin.'}, status=400)

        # Role validation
        if role and user.role != role:
            return Response({'error': f'User is not a {role}'}, status=400)

        # Law firm verification
        if user.role == 'lawfirm':
            if not hasattr(user, 'lawfirmprofile'):
                return Response({'error': 'Law firm profile not found'}, status=400)
            if registration_no and user.lawfirmprofile.registration_no != registration_no:
                return Response({'error': 'Invalid registration number'}, status=400)

        # Admin verification
        elif user.role == 'admin':
            if not hasattr(user, 'adminprofile'):
                return Response({'error': 'Admin profile not found'}, status=400)
            if not secret_key:
                return Response({'error': 'Secret key required for admin login'}, status=400)
            if not user.adminprofile.check_secret_key(secret_key):
                return Response({'error': 'Invalid admin secret key'}, status=400)
            
            # ✅ Ensure admin has correct permissions on login
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Get profile info
        is_onboarded = True
        status = 'approved'
        
        if user.role == 'client' and hasattr(user, 'clientprofile'):
            profile = user.clientprofile
            is_onboarded = getattr(profile, 'is_onboarded', True)
            status = getattr(profile, 'status', 'approved')
        elif user.role == 'lawfirm' and hasattr(user, 'lawfirmprofile'):
            profile = user.lawfirmprofile
            is_onboarded = getattr(profile, 'is_onboarded', True)
            status = getattr(profile, 'status', 'approved')

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'is_onboarded': is_onboarded,
                'status': status,
            }
        })


# ✅ NEW: Fix existing admin users (run via API endpoint or management command)
class FixAdminPermissionsView(APIView):
    permission_classes = [AllowAny]  # Change to IsAdminUser in production
    
    def post(self, request):
        secret = request.data.get('secret_key')
        
        # Security check - only allow with master secret
        if secret != 'advocare-master-2024':
            return Response({'error': 'Unauthorized'}, status=401)
        
        admins = User.objects.filter(role='admin')
        updated_count = 0
        
        for admin in admins:
            if not admin.is_staff or not admin.is_superuser:
                admin.is_staff = True
                admin.is_superuser = True
                admin.is_active = True
                admin.save()
                updated_count += 1
        
        return Response({
            'message': f'Fixed {updated_count} admin users',
            'total_admins': admins.count(),
            'updated': updated_count
        })