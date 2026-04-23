# from django.urls import path
# from .views import (
#     ClientOnboardingView,
#     LawfirmOnboardingView,
#     PendingClientsView,
#     ApproveClientView,
#     RejectClientView,
#     ClientDashboardView,
#     LawfirmDashboardView,
#     AdminOnboardingView,
#     ClientProfileView,
#     AdminDashboardView,
#     ClientStatusView  # Add this
# )

# urlpatterns = [
#     path('client-onboarding/', ClientOnboardingView.as_view(), name='client-onboarding'),
#     path('lawfirm-onboarding/', LawfirmOnboardingView.as_view(), name='lawfirm-onboarding'),
#     path('admin-onboarding/', AdminOnboardingView.as_view(), name='admin-onboarding'),
#     path('pending-clients/', PendingClientsView.as_view(), name='pending-clients'),
#     path('approve-client/<int:id>/', ApproveClientView.as_view(), name='approve-client'),
#     path('reject-client/<int:id>/', ApproveClientView.as_view(), name='reject-client'),  # Fixed: was pointing to ApproveClientView
#     path('client-dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
#     path('lawfirm-dashboard/', LawfirmDashboardView.as_view(), name='lawfirm-dashboard'),
#     path('client-profile/', ClientProfileView.as_view(), name='client-profile'),
#     path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),  # Add this
#     path('client-status/', ClientStatusView.as_view(), name='client-status'),  # Add this
# ]


from django.urls import path
from .views import (
    ClientOnboardingView,
    LawfirmOnboardingView,
    AdminOnboardingView,
    PendingClientsView,
    PendingLawFirmsView,
    ApproveClientView,
    RejectClientView,
    ApproveLawFirmView,
    RejectLawFirmView,
    ClientDashboardView,
    LawfirmDashboardView,
    AdminDashboardView,
    ClientProfileView,
    LawfirmProfileView,
    AdminProfileView,
    ClientStatusView,
    LawfirmStatusView,
    LawFirmsListView,  # Add this
    AuthMeView,        # Add this
    ClientProfileUpdateView,
    change_password,
    admin_all_clients, admin_all_lawfirms, admin_analytics, admin_dashboard_stats
)

urlpatterns = [
    # Onboarding
    path('client-onboarding/', ClientOnboardingView.as_view(), name='client-onboarding'),
    path('lawfirm-onboarding/', LawfirmOnboardingView.as_view(), name='lawfirm-onboarding'),
    path('admin-onboarding/', AdminOnboardingView.as_view(), name='admin-onboarding'),
    
    # Pending requests (Admin)
    path('pending-clients/', PendingClientsView.as_view(), name='pending-clients'),
    path('pending-lawfirms/', PendingLawFirmsView.as_view(), name='pending-lawfirms'),
    
    # Approve/Reject (Admin)
    path('approve-client/<int:id>/', ApproveClientView.as_view(), name='approve-client'),
    path('reject-client/<int:id>/', RejectClientView.as_view(), name='reject-client'),
    path('approve-lawfirm/<int:id>/', ApproveLawFirmView.as_view(), name='approve-lawfirm'),
    path('reject-lawfirm/<int:id>/', RejectLawFirmView.as_view(), name='reject-lawfirm'),
    
    # Dashboards
    path('client-dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
    path('lawfirm-dashboard/', LawfirmDashboardView.as_view(), name='lawfirm-dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Profiles
    path('client-profile/', ClientProfileView.as_view(), name='client-profile'),
    path('lawfirm-profile/', LawfirmProfileView.as_view(), name='lawfirm-profile'),
    path('admin-profile/', AdminProfileView.as_view(), name='admin-profile'),
    
    # Status
    path('client-status/', ClientStatusView.as_view(), name='client-status'),
    path('lawfirm-status/', LawfirmStatusView.as_view(), name='lawfirm-status'),

    # Law Firms List (for clients)
    path('lawfirms/', LawFirmsListView.as_view(), name='lawfirms-list'),
    path('lawfirms/approved/', LawFirmsListView.as_view(), name='lawfirms-approved'),
    
    # Auth
    path('auth/me/', AuthMeView.as_view(), name='auth-me'),

    path('client-profile/update/', ClientProfileUpdateView.as_view(), name='client-profile-update'),

    path('all-clients/', admin_all_clients, name='admin-all-clients'),
    path('all-lawfirms/', admin_all_lawfirms, name='admin-all-lawfirms'),
    path('admin-analytics/', admin_analytics, name='admin-analytics'),
    path('admin-dashboard/', admin_dashboard_stats, name='admin-dashboard-stats'),


    path('change-password/', change_password, name='change-password'),
]