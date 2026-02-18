from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def client_onboarding(request):
    return render(request, 'clients/client-onboarding.html')
