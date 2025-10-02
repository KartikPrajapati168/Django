from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import restaurant_create_view
from django.shortcuts import render, redirect
#razorpay 
from .views import create_razorpay_order, payment_success

 # Add app name if needed
app_name = 'restaurants'  # Add this if you're using namespaces

urlpatterns = [
    # path('admins/dashboard/', views.dashboard_redirect_view, name='dashboard_fallback'),
    path('admins/dashboard/<slug:slug>/', views.dashboard_view, name='dashboard'),
    path('admins/menus/<slug:slug>/', views.menu_view, name='menu'),
    
    path("admins/menus/<slug:slug>/add-category/", views.add_category, name="add_category"),
    # path("<slug:slug>/category/<int:category_id>/edit/", views.edit_category, name="edit_category"),
    path("admins/menus/<slug:slug>/edit-category/<int:category_id>/", views.edit_category, name="edit_category"),
    path("admins/menus/<slug:slug>/delete-category/<int:category_id>/", views.delete_category, name="delete_category"),
    path("admins/menus/<slug:slug>/add-item/", views.add_menu_item, name="add_menu_item"),
    path("admins/menus/<slug:slug>/delete-item/<int:item_id>/", views.delete_menu_item, name="delete_menu_item"),
    # path("<slug:slug>/item/<int:item_id>/edit/", views.edit_menu_item, name="edit_menu_item"),
    path('admins/menus/<slug:slug>/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    
    path('admins/orders/<slug:slug>/', views.order_view, name='order'),
    path('admins/tables/<slug:slug>/', views.table_view, name='table'),
    path('admins/profile/<slug:slug>/', views.profile_view, name='profile'),
    path('admins/feedbacks/<slug:slug>/', views.feedback_view, name='feedback'),
    path('admins/users/<slug:slug>/', views.users_view, name='user'),
    path('restaurant/profile/settings/', views.profile_settings_view, name='restaurant_profile_settings'),
    # path(
    #      '<int:restaurant_id>/book-table/',
    #     views.book_table,
    #     name='book_table'
    # ),
    path('spots/<slug:slug>/', views.restaurant_detail, name='restaurant_detail'),
    path('add/', views.restaurant_create_view, name='owner-restaurant-add'),
    # path('index/spots/', views.trending_spots, name='trending_spots'),
    # path('index/cuisine/<str:cuisine>/', views.cuisine_page, name='cuisine_page'),
    # Rename <str:cuisine> → <slug:slug> (slug = unique field from CuisinePageContent)
    path('index/cuisine/<slug:slug>/', views.cuisine_page, name='cuisine_page'),
    
    # Cuisine-wise: /spots/<slug>/book-table/
    path('spots/<slug:slug>/book-table/', views.book_table_view, name='book_table_cuisine'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name="table_booking_confirmation"),
    # Homepage: /book-table/<slug>/
    path('book-table/<slug:slug>/', views.book_table_view, name='book_table_index'), 
    
    # path('select-restaurant/', views.select_restaurant, name='select_restaurant'),
    path('restaurant-approval-pending/', views.approval_pending, name='restaurant_approval_pending'),
    #Redirect old dashboard URL to selection
    # path('admins/dashboard/', lambda request: redirect('select_restaurant'), name='dashboard'),
    
    path('create/', views.create_order, name='create_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('place_order/', views.place_order, name='place_order'),
    
    
    # path('submit_review/<int:restaurant_id>/', views.submit_review, name='submit_review'),
    # FIXED: Review submission URL - using slug instead of restaurant_id
    path('spots/<slug:slug>/submit-review/', views.submit_review, name='submit_review'),
    
    #for razorpay payment
    path('create-razorpay-order', create_razorpay_order, name='create_razorpay_order'),
    path('payment-success', payment_success, name='payment_success'),
]


