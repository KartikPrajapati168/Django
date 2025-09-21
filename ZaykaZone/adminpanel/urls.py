from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-alerts/', views.admin_alert_view, name='admin_alerts'),
    path('admin-orders/', views.admin_orders_view, name='admin_orders'),
    path('admin-restaurants/', views.admin_restaurants_view, name='admin_restaurants'),
    path('admin-table_booking/', views.admin_table_booking_view, name='admin_table_booking'),
    path('admin-users/', views.admin_users_view, name='admin_users'),
    
    path('admin-approve/<int:pk>/', views.approve_restaurant, name='approve_restaurant'),
    path('admin-reject/<int:pk>/', views.reject_restaurant, name='reject_restaurant'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='authentication/loginsignup/'), name='logout'),
]
