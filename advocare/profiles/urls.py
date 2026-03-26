from django.urls import path
from .views import (
    PendingClientsView,
    ApproveClientView,
    RejectClientView,
    ClientDashboardView,
    LawfirmDashboardView
)

urlpatterns = [
    path("pending-clients/", PendingClientsView.as_view()),
    path("approve-client/<int:id>/", ApproveClientView.as_view()),
    path("reject-client/<int:id>/", RejectClientView.as_view()),
    path("client-dashboard/", ClientDashboardView.as_view()),
    path("lawfirm-dashboard/", LawfirmDashboardView.as_view()),
]
