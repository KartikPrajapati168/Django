from django.urls import path
from .views import RegisterView,LoginView,FixAdminPermissionsView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('fix-admin-permissions/', FixAdminPermissionsView.as_view(), name='fix-admin-permissions'),
]

