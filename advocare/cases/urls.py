# from django.urls import path
# from .views import (
#     MyCasesView
# )

# urlpatterns = [
#     path('my-cases/', MyCasesView.as_view(), name='my-cases'),
#     # path('lawfirm-stats/', views.lawfirm_stats, name='lawfirm-stats'),
#     # path('case-requests/', views.case_requests, name='case-requests'),
#     # path('assigned-cases/', views.assigned_cases, name='assigned-cases'),
#     # path('court-updates/', views.court_updates, name='court-updates'),
#     # path('accept-request/<int:id>/', views.accept_request, name='accept-request'),
#     # path('reject-request/<int:id>/', views.reject_request, name='reject-request'),
#     # path('create/', views.create_case, name='create-case'),
# ]

from django.urls import path
from . import views
from .views import (
    PendingCaseRequestsView,AcceptCaseRequestView,RejectCaseRequestView,CaseAIAnalyzeView
    )
from . import views

urlpatterns = [
    # Case endpoints
    path('', views.CaseListCreateView.as_view(), name='case-list-create'),
    path('<int:pk>/', views.CaseDetailUpdateView.as_view(), name='case-detail'),
    path('my-cases/', views.MyCasesView.as_view(), name='my-cases'),
    path('<int:pk>/assign/', views.AssignCaseView.as_view(), name='assign-case'),

    path('pending-requests/', PendingCaseRequestsView.as_view(), name='pending-requests'),
    path('<int:case_id>/accept/', AcceptCaseRequestView.as_view(), name='accept-case'),
    path('<int:case_id>/reject/', RejectCaseRequestView.as_view(), name='reject-case'),

    path('lawfirm-stats/', views.lawfirm_stats, name='lawfirm-stats'),
    path('pending-requests/', views.pending_requests, name='pending-requests'),
    path('<int:case_id>/accept/', views.accept_case, name='accept-case'),
    path('<int:case_id>/reject/', views.reject_case, name='reject-case'),
    path('assigned-cases/', views.assigned_cases, name='assigned-cases'),
    path('accepted-cases/', views.accepted_cases, name='accepted-cases'),
    path('lawfirm-lawyers/', views.lawfirm_lawyers, name='lawfirm-lawyers'),
    path('add-lawyer/', views.add_lawyer, name='add-lawyer'),
    path('court-updates/', views.court_updates, name='court-updates'),

    path('monthly-stats/', views.monthly_case_stats, name='monthly-stats'),

    path('<int:case_id>/close/', views.close_case, name='close-case'),

    path('lawfirm-lawyers/<int:member_id>/', views.delete_team_member, name='delete-team-member'),

    path('all-cases/', views.admin_all_cases, name='admin-all-cases'),
    path('assigned-all/', views.admin_assigned_all, name='admin-assigned-all'),
    path('disputes/', views.admin_disputes, name='admin-disputes'),
    path('admin-court-update/', views.admin_court_update, name='admin-court-update'),


    path('<int:case_id>/ai-analyze/', CaseAIAnalyzeView.as_view(), name='case-ai-analyze'),
]