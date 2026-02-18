# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import authenticate, login
# from rest_framework_simplejwt.tokens import RefreshToken
# from .serializers import RegisterSerializer


# @api_view(['POST'])
# def register_view(request):

#     serializer = RegisterSerializer(data=request.data)

#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "User registered successfully"})
    
#     return Response(serializer.errors, status=400)


# @api_view(['POST'])
# def login_view(request):

#     username = request.data.get("username")
#     password = request.data.get("password")

#     user = authenticate(username=username, password=password)

#     if user is None:
#         return Response({"error": "Invalid credentials"}, status=400)

#     # Create session
#     login(request, user)

#     # Generate JWT
#     refresh = RefreshToken.for_user(user)

#     return Response({
#         "message": "Login successful",
#         "access_token": str(refresh.access_token),
#         "refresh_token": str(refresh),
#         "role": user.role
#     })



# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required

# def login_signup_view(request):
#     if request.user.is_authenticated:
#         # Redirect based on role (adjust URLs as needed)
#         if request.user.role == 'admin':
#             return redirect('admin_dashboard')
#         elif request.user.role == 'lawyer':
#             return redirect('lawyer_dashboard')
#         elif request.user.role == 'client':
#             return redirect('client_onboarding')
#     return render(request, 'authentication/loginsignup.html')



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer


# 🔹 REGISTER API
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response({
            "success": True,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# 🔹 LOGIN API
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({
            "error": "Username and password required"
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # 🔥 Generate JWT Tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "message": "Login successful",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "role": user.role
    }, status=status.HTTP_200_OK)


from django.shortcuts import render, redirect

def login_signup_view(request):
    return render(request, 'authentication/loginsignup.html')
