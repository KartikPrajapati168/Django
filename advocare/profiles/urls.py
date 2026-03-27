from django.urls import path
from .views import (
    ClientOnboardingView,
    LawfirmOnboardingView,
    PendingClientsView,
    ApproveClientView,
    RejectClientView,
    ClientDashboardView,
    LawfirmDashboardView,
    AdminOnboardingView,   # we'll create this
)

urlpatterns = [
    path('client-onboarding/', ClientOnboardingView.as_view(), name='client-onboarding'),
    path('lawfirm-onboarding/', LawfirmOnboardingView.as_view(), name='lawfirm-onboarding'),
    path('admin-onboarding/', AdminOnboardingView.as_view(), name='admin-onboarding'),
    path('pending-clients/', PendingClientsView.as_view(), name='pending-clients'),
    path('approve-client/<int:id>/', ApproveClientView.as_view(), name='approve-client'),
    path('reject-client/<int:id>/', RejectClientView.as_view(), name='reject-client'),
    path('client-dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
    path('lawfirm-dashboard/', LawfirmDashboardView.as_view(), name='lawfirm-dashboard'),
]