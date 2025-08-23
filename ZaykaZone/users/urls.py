from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('authentication/loginsignup/', views.login_signup, name='login_signup'),
    # path('book-table/', views.book_table, name='book_table'),
    path('contact-submit/', views.contact_submit, name='contact_submit'),
    path('index/',views.index,name='index'),
    path('index/asian/',views.index_asian,name='index_asian'),
    path('index/buffets/',views.index_buffets,name='index_buffets'),
    path('index/gujarati/',views.index_gujarati,name='index_gujarati'),
    path('index/legendary/',views.index_legendary,name='index_legendary'),
    path('index/spots/pepito/',views.index_pepito,name='index_pepito'),
    path('index/rollins/',views.index_rollins,name='index_rollins'),
    path('index/spots/',views.index_spots,name='index_spots'),
    path('index/starter_page/',views.index_starterpage,name='index_starterpage'),
    path('register', views.register_user, name='register'),
    path('login', views.login_user, name='login'),
    
    path('after-login/', views.after_login_redirect, name='after_login_redirect'),
    path('select-restaurant/', views.select_restaurant_view, name='select_restaurant'),
    
    # Newly added routes
    path('logout/', views.logout_view, name='logout'),
    path('switch-account/', views.switch_account, name='switch_account'),
    
    # path('index/<str:cuisine_slug>/', views.cuisine_view, name='cuisine_spots'),
]
