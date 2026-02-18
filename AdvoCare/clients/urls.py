from django.urls import path
from .views import client_onboarding

urlpatterns = [
    path('client-onboarding/', client_onboarding, name='client_onboarding'),
]
