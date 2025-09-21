from django.shortcuts import render
from restaurants.models import RestaurantApprovalRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect, get_object_or_404
from restaurants.models import TableBooking
from restaurants.models import Restaurant# apne model ka path check karna

def admin_dashboard_view(request):
    return render(request, 'adminpanel/admin-dashboard.html')  # template path

@login_required
def admin_alert_view(request):
    # Get only unresolved approval requests
    # approval_requests = RestaurantApprovalRequest.objects.filter(is_resolved=False).select_related("restaurant", "restaurant__owner").order_by("-created_at")
    # return render(request, "adminpanel/admin-alerts.html", {"approval_requests": approval_requests})
    
    # Pending approvals
    pending_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_resolved=False, is_approved=False, is_rejected=False)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    # Approved restaurants
    approved_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_approved=True)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    # Rejected restaurants
    rejected_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_rejected=True)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    return render(request, "adminpanel/admin-alerts.html", {
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
    })

from django.core.paginator import Paginator
from restaurants.models import Order, OrderItem

def admin_orders_view(request):
    orders = (
        Order.objects
        .select_related('user', 'restaurant')
        .prefetch_related('order_items')
        .order_by('-timestamp')
    )
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'adminpanel/admin-orders.html', {
        'orders': page_obj
    })


from django.db.models import Prefetch
from restaurants.models import RestaurantOwnerProfile, RestaurantApprovalRequest

def admin_restaurants_view(request):
    # Prefetch RestaurantOwnerProfile through the owner (User) relationship
    owner_profile_prefetch = Prefetch(
        'owner__owner_profiles',  # Navigate from Restaurant.owner to User.owner_profiles
        queryset=RestaurantOwnerProfile.objects.all(),
        to_attr='profile_list'    # Store as a list in case multiple profiles exist (though OneToOne should limit to one)
    )

    # Fetch approved restaurants
    restaurants = (
        Restaurant.objects
        .select_related('owner')                  # Join with User
        .prefetch_related(owner_profile_prefetch) # Prefetch owner profiles
        .filter(is_approved=True)                # Only approved restaurants
        .order_by('-created_at')
    )

    # Fetch restaurant approval requests
    booking_profile_prefetch = Prefetch(
        'restaurant__owner_profile',
        queryset=RestaurantOwnerProfile.objects.all(),
        to_attr='profile_obj'
    )

    restaurants_booking = (
        RestaurantApprovalRequest.objects
        .select_related('restaurant', 'restaurant__owner')
        .prefetch_related(booking_profile_prefetch)
        .order_by('-created_at')
    )

    return render(request, 'adminpanel/admin-restaurants.html', {
        'restaurants': restaurants,
        'restaurant_booking': restaurants_booking
    })
    


def admin_table_booking_view(request):
    table_bookings = TableBooking.objects.all().order_by('-created_at')  # latest first
    return render(request, 'adminpanel/admin-table_booking.html', {
        'table_bookings': table_bookings
    })

from users.models import User

def admin_users_view(request):
    # Fetch all users with relevant fields
    users = User.objects.all().order_by('-created_at')  # Order by creation date (newest first)

    return render(request, 'adminpanel/admin-users.html', {
        'users': users
    })


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

