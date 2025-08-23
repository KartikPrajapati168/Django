from django.shortcuts import render
from restaurants.models import RestaurantApprovalRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect, get_object_or_404

def admin_dashboard_view(request):
    return render(request, 'adminpanel/admin-dashboard.html')  # template path

@login_required
def admin_alert_view(request):
    # Get only unresolved approval requests
    approval_requests = RestaurantApprovalRequest.objects.filter(is_resolved=False).select_related("restaurant", "restaurant__owner").order_by("-created_at")
    return render(request, "adminpanel/admin-alerts.html", {"approval_requests": approval_requests})

def admin_orders_view(request):
    return render(request, 'adminpanel/admin-orders.html')

def admin_restaurants_view(request):
    return render(request, 'adminpanel/admin-restaurants.html')

def admin_table_booking_view(request):
    return render(request, 'adminpanel/admin-table_booking.html')

def admin_users_view(request):
    return render(request, 'adminpanel/admin-users.html')


@login_required
def approve_restaurant(request, pk):
    request_obj = get_object_or_404(RestaurantApprovalRequest, pk=pk)
    request_obj.is_approved = True
    request_obj.is_rejected = False  # Optional: clear reject flag
    request_obj.restaurant.is_approved = True
    request_obj.restaurant.save()
    request_obj.save()
    messages.success(request, "Restaurant approved ✅")
    return redirect('adminpanel:admin_alerts')


@login_required
def reject_restaurant(request, pk):
    request_obj = get_object_or_404(RestaurantApprovalRequest, pk=pk)
    request_obj.is_rejected = True
    request_obj.is_approved = False  # Optional: clear approve flag
    request_obj.restaurant.is_approved = False  # Explicitly mark it unapproved
    request_obj.restaurant.save()
    request_obj.save()
    messages.error(request, "Restaurant rejected ❌")
    return redirect('adminpanel:admin_alerts')

