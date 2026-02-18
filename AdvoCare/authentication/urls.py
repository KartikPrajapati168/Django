from django.urls import path
from .views import register_view, login_view,login_signup_view

app_name = 'authentication'

urlpatterns = [
    path('login-signup/', login_signup_view, name='login_signup'),          # serves the page
    path('register/', register_view,name="register"),
    path('login/', login_view,name="login"),
]
