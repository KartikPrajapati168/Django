# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from allauth.socialaccount.models import SocialApp



def log(request):
    return render(request, 'index.html')


def google_redirect(request):
    return redirect('https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?client_id=42284273460-uvhfgf3cp50qjcijhigcpji49f14ae0o.apps.googleusercontent.com&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Faccounts%2Fgoogle%2Flogin%2Fcallback%2F&scope=profile%20email&response_type=code&state=DfzrJdxeYxbj38dh&access_type=online&service=lso&o2v=2&flowName=GeneralOAuthFlow')
    
    # try:
    #     app = SocialApp.objects.get(provider='google')
    # except SocialApp.DoesNotExist:
    #     return HttpResponse("Google SocialApp is not configured in the admin panel.", status=500)

    # client_id = app.client_id
    # redirect_uri = request.build_absolute_uri(reverse('account_google_login'))

    # url = (
    #     "https://accounts.google.com/o/oauth2/v2/auth"
    #     "?client_id={client_id}"
    #     "&redirect_uri={redirect_uri}"
    #     "&scope=profile email"
    #     "&response_type=code"
    #     "&access_type=online"
    # ).format(client_id=client_id, redirect_uri=redirect_uri)

    # return redirect(url)