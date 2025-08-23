from django.shortcuts import render,redirect, get_object_or_404

from .models import Restaurant,Review,RestaurantImage,CartItem     # Restaurant model
from .forms import TableBookingForm     # ModelForm you’ll create below
from .utils import extract_from_text, CUISINES, CITIES
from django.contrib.auth.decorators import login_required
from .models import RestaurantOwnerProfile,TableBooking,MenuItem,MenuCategory
from .forms import RestaurantForm, OwnerProfileForm
from django.contrib import messages
from adminpanel.models import CuisinePageContent  # import from adminpanel
from .models import RestaurantApprovalRequest,Order,OrderItem
from django.db.models import Sum
from users.models import User
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard_view(request, slug):
    # Get restaurant with security checks
    restaurant = get_object_or_404(
        Restaurant, 
        slug=slug, 
        # owner=request.user,
        owner_name__iexact=request.user.full_name,  # Case-insensitive match
        is_approved=True
    )
    
    # Get approval status
    approval_request = RestaurantApprovalRequest.objects.filter(
        restaurant=restaurant
    ).first()
    
    # Get menu data
    menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    
    # Get bookings (today and upcoming)
    today = timezone.now().date()
    upcoming_bookings = TableBooking.objects.filter(
        restaurant=restaurant,
        date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')[:5]
    
    # Get recent reviews
    recent_reviews = Review.objects.filter(
        restaurant=restaurant
    ).order_by('-created_at')[:5]
    
    # Get recent orders (last 7 days)
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_orders = Order.objects.filter(
        restaurant=restaurant,
        timestamp__gte=one_week_ago
    ).order_by('-timestamp')[:10]
    
    # Get preview images
    preview_images = RestaurantImage.objects.filter(
        restaurant=restaurant,
        is_preview=True
    )[:4]
    
    # Calculate pending orders count
    pending_orders_count = Order.objects.filter(
        restaurant=restaurant,
        status__in=['pending', 'confirmed', 'preparing']
    ).count()
    
    # Get owner profile
    try:
        owner_profile = request.user.owner_profile
    except RestaurantOwnerProfile.DoesNotExist:
        owner_profile = None
    
    # Get cart items count for user
    cart_items_count = CartItem.objects.filter(user=request.user).count()
    
    # Get all user's restaurants for switcher
    user_restaurants = Restaurant.objects.filter(
        owner=request.user,
        is_approved=True
    )
    
    context = {
        'owner_profile': owner_profile,
        'restaurant': restaurant,
        'approval_request': approval_request,
        'menu_categories_count': menu_categories.count(),
        'menu_items_count': menu_items.count(),
        'upcoming_bookings': upcoming_bookings,
        'upcoming_bookings_count': upcoming_bookings.count(),
        'recent_reviews': recent_reviews,
        'recent_reviews_count': recent_reviews.count(),
        'recent_orders': recent_orders,
        'recent_orders_count': recent_orders.count(),
        'preview_images': preview_images,
        'pending_orders_count': pending_orders_count,
        'cart_items_count': cart_items_count,
        'user_restaurants': user_restaurants,
    }
    
    return render(request, 'restaurants/admins/dashboard.html', context)


# def dashboard_redirect_view(request):
#     # redirect to select restaurant or default dashboard
#     restaurant = Restaurant.objects.filter(owner=request.user).first()
#     if restaurant:
#         return redirect('restaurants:dashboard', slug=restaurant.slug)
#     return redirect('select_restaurant')  # fallback


# Approval pending page
@login_required
def approval_pending(request):
    # Get any pending approval requests
    pending_requests = RestaurantApprovalRequest.objects.filter(
        restaurant__owner=request.user,
        is_approved=False
    )
    
    return render(request, 'restaurants/admins/restaurant_approval_pending.html', {
        'pending_requests': pending_requests
    })
    

# @login_required
# def dashboard_view(request):
#     # Get owner profile and restaurants
#     try:
#         owner_profile = request.user.owner_profile
#     except RestaurantOwnerProfile.DoesNotExist:
#         owner_profile = None
    
#     restaurants = Restaurant.objects.filter(owner=request.user).order_by('-created_at')
    
#     dashboard_data = []
    
#     for restaurant in restaurants:
#         # Get approval status
#         approval_request = RestaurantApprovalRequest.objects.filter(
#             restaurant=restaurant
#         ).first()
        
#         # Get menu data
#         menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
#         menu_items = MenuItem.objects.filter(restaurant=restaurant)
        
#         # Get bookings (today and upcoming)
#         today = timezone.now().date()
#         upcoming_bookings = TableBooking.objects.filter(
#             restaurant=restaurant,
#             date__gte=today,
#             status__in=['pending', 'confirmed']
#         ).order_by('date', 'time')[:5]
        
#         # Get recent reviews
#         recent_reviews = Review.objects.filter(
#             restaurant=restaurant
#         ).order_by('-created_at')[:5]
        
#         # Get recent orders (last 7 days)
#         one_week_ago = timezone.now() - timedelta(days=7)
#         recent_orders = Order.objects.filter(
#             restaurant=restaurant,
#             timestamp__gte=one_week_ago
#         ).order_by('-timestamp')[:10]
        
#         # Get preview images
#         preview_images = RestaurantImage.objects.filter(
#             restaurant=restaurant,
#             is_preview=True
#         )[:4]
        
#         # Calculate pending orders count
#         pending_orders_count = Order.objects.filter(
#             restaurant=restaurant,
#             status__in=['pending', 'confirmed', 'preparing']
#         ).count()
        
#         dashboard_data.append({
#             'restaurant': restaurant,
#             'approval_request': approval_request,
#             'menu_categories_count': menu_categories.count(),
#             'menu_items_count': menu_items.count(),
#             'upcoming_bookings': upcoming_bookings,
#             'upcoming_bookings_count': upcoming_bookings.count(),
#             'recent_reviews': recent_reviews,
#             'recent_reviews_count': recent_reviews.count(),
#             'recent_orders': recent_orders,
#             'recent_orders_count': recent_orders.count(),
#             'preview_images': preview_images,
#             'pending_orders_count': pending_orders_count,
#         })
    
#     # Get cart items count for user
#     cart_items_count = CartItem.objects.filter(user=request.user).count()
    
#     context = {
#         'owner_profile': owner_profile,
#         'dashboard_data': dashboard_data,
#         'total_restaurants': restaurants.count(),
#         'cart_items_count': cart_items_count,
#     }
    
#     return render(request, 'restaurants/admins/dashboard.html', context)


# def dashboard_view(request):
#     restaurant = Restaurant.objects.filter(owner=request.user).first()

#     if not restaurant:
#         messages.warning(request, "Pehle profile complete karo.")
#         return redirect("restaurants:restaurant_profile_settings")

#     if not restaurant.is_approved:
#         messages.info(request, "Aapki request abhi pending hai. Admin approval ke baad dashboard access milega.")
#         return redirect("restaurants:restaurant_profile_settings")
    
#     # Calculate statistics
#     total_users = User.objects.filter(order__restaurant=restaurant).distinct().count()
#     revenue = Order.objects.filter(restaurant=restaurant, status='completed').aggregate(
#         total_revenue=Sum('total_amount')
#     )['total_revenue'] or 0
#     orders_count = Order.objects.filter(restaurant=restaurant).count()
#     reviews_count = Feedback.objects.filter(restaurant=restaurant).count()
#     bookings_count = TableBooking.objects.filter(restaurant=restaurant).count()
    
#     # Recent activity
#     recent_orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')[:5]
#     recent_bookings = TableBooking.objects.filter(restaurant=restaurant).order_by('-booking_time')[:5]
#     recent_feedbacks = Feedback.objects.filter(restaurant=restaurant).order_by('-created_at')[:5]
    
#     # Combine activities
#     activities = []
#     for order in recent_orders:
#         activities.append({
#             'type': 'order',
#             'user': order.user,
#             'message': 'Order placed',
#             'time': order.created_at,
#             'details': f"Order #{order.id}"
#         })
    
#     for booking in recent_bookings:
#         activities.append({
#             'type': 'booking',
#             'user': booking.user,
#             'message': 'Table booked',
#             'time': booking.booking_time,
#             'details': f"{booking.guests} guests"
#         })
    
#     for feedback in recent_feedbacks:
#         activities.append({
#             'type': 'feedback',
#             'user': feedback.user,
#             'message': 'Feedback submitted',
#             'time': feedback.created_at,
#             'details': f"Rating: {feedback.rating}/5"
#         })
    
#     # Sort activities by time
#     activities = sorted(activities, key=lambda x: x['time'], reverse=True)[:5]
    
#     # Recent orders for table
#     recent_orders_table = Order.objects.filter(restaurant=restaurant).order_by('-created_at')[:10]
    
#     # Top products
#     top_products = MenuItem.objects.filter(restaurant=restaurant).annotate(
#         total_ordered=Sum('orderitem__quantity')
#     ).order_by('-total_ordered')[:4]
    
#     context = {
#         'restaurant': restaurant,
#         'total_users': total_users,
#         'revenue': revenue,
#         'orders_count': orders_count,
#         'reviews_count': reviews_count,
#         'bookings_count': bookings_count,
#         'activities': activities,
#         'recent_orders': recent_orders_table,
#         'top_products': top_products,
#     }
    
#     return render(request, "restaurants/admins/dashboard.html", context)

def menu_view(request, slug):
    # Get the restaurant based on the slug
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    # Get menu items and categories for this restaurant
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    
    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'categories': categories
    }
    return render(request, 'restaurants/admins/menus.html', context)

from django.shortcuts import redirect
from .forms import MenuCategoryCreateForm

def add_category(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == 'POST':
        form = MenuCategoryCreateForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            return redirect('restaurants:menu', slug=restaurant.slug)
    else:
        form = MenuCategoryCreateForm()
    
    return render(request, 'restaurants/admins/add_category.html', {
        'form': form,
        'restaurant': restaurant
    })
    
from .forms import MenuItemCreateForm

def edit_menu_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    menu_item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    
    if request.method == 'POST':
        form = MenuItemCreateForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('restaurants:menu', slug=restaurant.slug)
    else:
        form = MenuItemCreateForm(instance=menu_item)
    
    return render(request, 'restaurants/admins/edit_menu_item.html', {
        'form': form,
        'restaurant': restaurant,
        'menu_item': menu_item
    })

def delete_menu_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    menu_item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('restaurants:menu', slug=restaurant.slug)
    
    return render(request, 'restaurants/admins/confirm_delete.html', {
        'restaurant': restaurant,
        'menu_item': menu_item
    })
    
def order_view(request,slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, 'restaurants/admins/orders.html', {'restaurant': restaurant})

def table_view(request,slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, 'restaurants/admins/tables.html', {'restaurant': restaurant})

def feedback_view(request,slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, 'restaurants/admins/feedbacks.html', {'restaurant': restaurant})

def users_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, 'restaurants/admins/users.html', {'restaurant': restaurant})

def profile_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, 'restaurants/admins/profile.html', {'restaurant': restaurant})


@login_required
def profile_settings_view(request):
    user = request.user
    restaurant = Restaurant.objects.filter(owner=user).first()
    # ✅ Redirect if already approved
    if restaurant:
        approval_obj = RestaurantApprovalRequest.objects.filter(restaurant=restaurant).first()
        if approval_obj and approval_obj.is_approved:
            return redirect("restaurants:dashboard")  # 🔁 Replace with your correct dashboard URL name
    owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        if not restaurant:
            restaurant = Restaurant(owner=user)

        # Restaurant fields
        restaurant.name = request.POST.get("name", "").strip()
        restaurant.description = request.POST.get("description", "").strip()
        restaurant.address = request.POST.get("address", "").strip()
        restaurant.timings = request.POST.get("timings", "").strip()
        restaurant.dining_out_available = 'dining_out' in request.POST

        # Extract if not already filled
        if not restaurant.cuisine:
            restaurant.cuisine = extract_from_text(restaurant.description, CUISINES)

        if not restaurant.city:
            restaurant.city = extract_from_text(restaurant.address, CITIES)

        # Handle logo upload
        if request.FILES.get("logo"):
            restaurant.logo = request.FILES["logo"]

        # Owner name logic
        updated_owner_name = request.POST.get("owner_name", "").strip()
        
        # ✅ Update owner_profile regardless
        owner_profile.full_name = updated_owner_name or user.full_name
        owner_profile.email = request.POST.get("owner_email", "").strip()
        owner_profile.phone = request.POST.get("owner_phone", "").strip()
        owner_profile.gst_number = request.POST.get("gst_number", "").strip()
        owner_profile.save()

        # ✅ Always sync restaurant.owner_name with updated profile name
        restaurant.owner_name = owner_profile.full_name
            
        restaurant.save()
        
        # Create approval request if it doesn’t exist
        if not RestaurantApprovalRequest.objects.filter(restaurant=restaurant).exists():
            RestaurantApprovalRequest.objects.create(restaurant=restaurant)

    #     messages.success(request, "Profile updated ✅")
    #     return redirect("restaurants:dashboard")

    # GET request – prefill
    init = {
        'name':        restaurant.name        if restaurant else '',
        'description': restaurant.description if restaurant else '',
        'address':     restaurant.address     if restaurant else '',
        'timings':     restaurant.timings     if restaurant else '',
        'dining_out_available': restaurant.dining_out_available if restaurant else False,

        'owner_name':  owner_profile.full_name or user.full_name,
        'owner_email': owner_profile.email     or user.email,
        'owner_phone': owner_profile.phone     or getattr(user, 'full_phone', ''),
        'gst_number':  owner_profile.gst_number or '',
    }

    return render(request, 'restaurants/admins/profile_settings.html', init)



# from django.shortcuts import redirect
# def custom_login_view(request):
#     user = request.user  # ✅ Get the logged-in user

#     if user.is_authenticated:  # ✅ Check if the user is authenticated
#         if user.role == "restaurant":  # ✅ Check the user's role
#             # Get approved restaurants for this user
#             approved_restaurants = user.restaurants.filter(approved=True)
#             count = approved_restaurants.count()
            
#             if count == 0:
#                 return redirect('no_restaurant_page')
#             elif count == 1:
#                 # Redirect to the admin dashboard of that single restaurant
#                 restaurant = approved_restaurants.first()
#                 return redirect('restaurant_dashboard', restaurant_id=restaurant.id)
#             else:
#                 # Redirect to the selection page
#                 return redirect('select_restaurant')
#         else:
#             # For other roles, redirect to their respective dashboard
#             return redirect('some_other_dashboard')
#     else:
#         # Handle unauthenticated access
#         return redirect('login')  # or wherever your login page is
    

# @login_required
# def select_restaurant(request):
#     # Get approved restaurants for current user
#     restaurants = Restaurant.objects.filter(
#         owner=request.user,
#         is_approved=True
#     )
    
#     # If no restaurants, redirect to approval pending
#     # if not restaurants.exists():
#     #     return redirect('restaurants:restaurant_approval_pending')
    
#     # If only one restaurant, redirect directly to its dashboard
#     if restaurants.count() == 1:
#         return redirect('restaurants:dashboard', restaurant_id=restaurants.first().id)
    
#     return render(request, 'restaurants/admins/restaurant_selection.html', {
#         'restaurants': restaurants
#     })
    
    
        
# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()
#     owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=user)

#     if request.method == "POST":
#         if not restaurant:
#             restaurant = Restaurant(owner=user)

#         # Restaurant fields
#         restaurant.name = request.POST.get("name")
#         restaurant.description = request.POST.get("description")
#         restaurant.address = request.POST.get("address")
#         restaurant.timings = request.POST.get("timings")
#         restaurant.dining_out_available = 'dining_out' in request.POST

#         if request.FILES.get("logo"):
#             restaurant.logo = request.FILES["logo"]

#         restaurant.save()

#         # RestaurantOwnerProfile fields (only stored here)
#         owner_profile.full_name = request.POST.get("owner_name")
#         owner_profile.email = request.POST.get("owner_email")
#         owner_profile.phone = request.POST.get("owner_phone")
#         owner_profile.gst_number = request.POST.get("gst_number")
#         owner_profile.save()

#         return redirect("restaurants:dashboard")

#     else:
#         # Prefill values from Restaurant and Owner Profile
#         initial_data = {
#             'name': restaurant.name if restaurant else '',
#             'description': restaurant.description if restaurant else '',
#             'address': restaurant.address if restaurant else '',
#             'timings': restaurant.timings if restaurant else '',
#             'dining_out_available': restaurant.dining_out_available if restaurant else False,
#             'owner_name': owner_profile.full_name or '',
#             'owner_email': owner_profile.email or '',
#             'owner_phone': owner_profile.phone or '',
#             'gst_number': owner_profile.gst_number or '',
#         }

#         return render(request, 'restaurants/admins/profile_settings.html', initial_data)


# @login_required
# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()
#     owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=user)

#     # ---------- POST ----------
#     if request.method == "POST":
#         form = RestaurantForm(request.POST,
#                               request.FILES,
#                               instance=restaurant)

#         # 👇 Owner‑profile को पहले ही अपडेट कर दें
#         owner_profile.full_name  = request.POST.get("owner_name", "").strip()
#         owner_profile.email      = request.POST.get("owner_email", "").strip()
#         owner_profile.phone      = request.POST.get("owner_phone", "").strip()
#         owner_profile.gst_number = request.POST.get("gst_number", "").strip()
#         owner_profile.save()

#         # अब RestaurantForm validate करें
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = user
#             restaurant.dining_out_available = (
#                 'dining_out' in request.POST
#             )

#             if request.FILES.get("logo"):
#                 restaurant.logo = request.FILES["logo"]

#             restaurant.save()
#             messages.success(request, "Profile saved ✅")
#             return redirect("restaurants:dashboard")

#         # –– form invalid → वही पेज दोबारा दिखाओ
#         messages.error(request, "कृपया फ़ॉर्म की ग़लतियाँ ठीक करें.")
#         return render(request,
#                       "restaurants/admins/profile_settings.html",
#                       {
#                           'form': form,
#                           'owner_name': owner_profile.full_name,
#                           'owner_email': owner_profile.email,
#                           'owner_phone': owner_profile.phone,
#                           'gst_number': owner_profile.gst_number,
#                           'dining_out_available':
#                               'dining_out' in request.POST,
#                       })

#     # ---------- GET ----------
#     form = RestaurantForm(instance=restaurant)
#     context = {
#         'form'      : form,
#         'owner_name': owner_profile.full_name  or user.full_name,
#         'owner_email': owner_profile.email     or user.email,
#         'owner_phone': owner_profile.phone     or getattr(user, 'full_phone', ''),
#         'gst_number' : owner_profile.gst_number or '',
#         'dining_out_available':
#             restaurant.dining_out_available if restaurant else False,
#     }
#     return render(request,
#                   "restaurants/admins/profile_settings.html",
#                   context)


# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()
#     owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=user)

#     if request.method == "POST":
#         if not restaurant:
#             restaurant = Restaurant(owner=user)

#         restaurant.name = request.POST.get("name")
#         restaurant.description = request.POST.get("description")
#         restaurant.address = request.POST.get("address")
#         restaurant.timings = request.POST.get("timings")
#         restaurant.dining_out_available = 'dining_out' in request.POST

#         # ✅ Save GST number in owner profile
#         owner_profile.gst_number = request.POST.get("gst_number")
#         owner_profile.save()

#         # ✅ Update editable user fields (if changed)
#         user.full_name = request.POST.get("owner_name")
#         user.email = request.POST.get("owner_email")
#         user.full_phone = request.POST.get("owner_phone")
#         user.save()

#         # ✅ Optional logo
#         if request.FILES.get("logo"):
#             restaurant.logo = request.FILES["logo"]

#         restaurant.save()
#         return redirect("restaurants:dashboard")

#     else:
#         # ✅ Prefill logic
#         initial_data = {
#             'gst_number': owner_profile.gst_number,
#             'owner_name': user.full_name,
#             'owner_email': user.email,
#             'owner_phone': user.full_phone,
#         }

#         if restaurant:
#             initial_data.update({
#                 'name': restaurant.name,
#                 'description': restaurant.description,
#                 'address': restaurant.address,
#                 'timings': restaurant.timings,
#                 'dining_out_available': restaurant.dining_out_available,
#             })

#         return render(request, 'restaurants/admins/profile_settings.html', initial_data)



# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()

#     if request.method == "POST":
#         if not restaurant:
#             restaurant = Restaurant(owner=user)

#         restaurant.name = request.POST.get("name")
#         restaurant.description = request.POST.get("description")
#         restaurant.address = request.POST.get("address")
#         restaurant.timings = request.POST.get("timings")
#         # Save GST number to owner profile
#         owner_profile = request.user.owner_profile
#         owner_profile.gst_number = request.POST.get('gst_number')
#         owner_profile.save()

#         # ✅ Dining out logic
#         restaurant.dining_out_available = 'dining_out' in request.POST

#         # ✅ Owner details – editable by form
#         restaurant.owner_name = request.POST.get("owner_name")
#         restaurant.owner_email = request.POST.get("owner_email")
#         restaurant.owner_phone = request.POST.get("owner_phone")

#         # ✅ Logo (optional)
#         if request.FILES.get("logo"):
#             restaurant.logo = request.FILES["logo"]

#         restaurant.save()
#         return redirect("restaurants:dashboard")  # or wherever

#     else:
#         # ✅ Prefill values from request.user only if restaurant doesn’t exist
#         initial_data = {}
#         if restaurant:
#             initial_data = {
#                 'name': restaurant.name,
#                 'description': restaurant.description,
#                 'address': restaurant.address,
#                 'timings': restaurant.timings,
#                 'gst_number': request.user.owner_profile.gst_number,  # ✅ Fetch for prefill
#                 'dining_out_available': restaurant.dining_out_available,
#                 'owner_name': restaurant.owner_name,
#                 'owner_email': restaurant.owner_email,
#                 'owner_phone': restaurant.owner_phone,
#             }
#         else:
#             # prefill from logged-in user if no restaurant yet
#             initial_data = {
#                 'owner_name': user.full_name,
#                 'owner_email': user.email,
#                 'owner_phone': user.full_phone,
#             }

#         return render(request, 'restaurants/admins/profile_settings.html', initial_data)

# @login_required
# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()
#     owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=user)

#     if request.method == 'POST':
#         form = RestaurantForm(request.POST, request.FILES, instance=restaurant)

#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = user
#             restaurant.dining_out_available = 'dining_out' in request.POST  # ✅ checkbox fix
#             restaurant.save()

#             # Update or create the owner profile
#             owner_profile.gst_number = request.POST.get('gst_number')
#             owner_profile.save()

#             return redirect('/restaurant/dashboard/')

#     else:
#         form = RestaurantForm(instance=restaurant)

#     # Pass context for pre-filling owner fields
#     context = {
#         'form': form,
#         'owner_name': user.full_name,
#         'owner_email': user.email,
#         'owner_phone': user.full_phone,
#         'gst_number': owner_profile.gst_number or ''
#     }

#     return render(request, 'restaurants/admins/profile_settings.html', context)

# @login_required
# def profile_settings_view(request):
#     user = request.user
#     restaurant = Restaurant.objects.filter(owner=user).first()

#     if request.method == 'POST':
#         form = RestaurantForm(request.POST, request.FILES, instance=restaurant)

#         if form.is_valid():
#             rest = form.save(commit=False)
#             rest.owner = user
#             rest.owner_name = request.POST.get('owner_name')
#             rest.owner_email = request.POST.get('owner_email')
#             rest.owner_phone = request.POST.get('owner_phone')
#             rest.gst_number = request.POST.get('gst_number')
#             rest.dining_out_available = 'dining_out' in request.POST  # ✅ FIX for checkbox
#             rest.save()
#             return redirect('/restaurant/dashboard/')
#     else:
#         form = RestaurantForm(instance=restaurant)

#     # Prefill from user model if restaurant is empty
#     context = {
#         'form': form,
#         'owner_name': restaurant.owner_name if restaurant else user.full_name,
#         'owner_email': restaurant.owner_email if restaurant else user.email,
#         'owner_phone': restaurant.owner_phone if restaurant else user.full_phone,
#         'gst_number': restaurant.gst_number if restaurant else ''
#     }

#     return render(request, 'restaurants/profile_settings.html', context)


# def book_table(request, restaurant_id):
#     restaurant = get_object_or_404(Restaurant, id=restaurant_id)

#     if request.method == "POST":
#         form = TableBookingForm(request.POST)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.restaurant = restaurant
#             if request.user.is_authenticated:
#                 booking.user = request.user
#             booking.save()

#             send_confirmation_email(booking)       # optional e‑mail
#             return redirect('booking_success')
#     else:
#         initial = {}
#         if request.user.is_authenticated:
#             initial = {
#                 'name':  request.user.get_full_name(),
#                 'email': request.user.email,
#                 'phone': request.user.phone,
#             }
#         form = TableBookingForm(initial=initial)

#     # IMPORTANT: render *users* template, not a restaurant template
#     return render(
#         request,
#         'users/user_side/index.html',          # ← your front‑end file
#         {'form': form, 'restaurant': restaurant}
#     )

import json

@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            restaurant_id = data.get('restaurant_id')
            items = data.get('items', [])
            
            # Calculate total price
            total_price = 0
            order_items = []
            
            for item in items:
                menu_item = MenuItem.objects.get(id=item['id'])
                total_price += menu_item.price * item['quantity']
                order_items.append({
                    'menu_item': menu_item,
                    'quantity': item['quantity'],
                    'price': menu_item.price
                })
            
            # Create order
            order = Order.objects.create(
                customer=request.user,
                restaurant_id=restaurant_id,
                total_price=total_price,
                status='pending'
            )
            
            # Create order items
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item['menu_item'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': 'Order placed successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)

def order_confirmation(request, order_id):
    # This will be implemented later
    order = get_object_or_404(Order, id=order_id, user=request.user)
    restaurant = order.restaurant   # order se restaurant nikala
    
    return render(request, 'users/user_side/order_confirmation.html', {'order': order,'restaurant':restaurant})



# @login_required(login_url='/login/')
# def place_order(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     if not cart_items.exists():
#         return redirect('/spots/pepito')   # empty cart se order nahi banega

#     total_price = sum(item.menu_item.price * item.quantity for item in cart_items)

#     order = Order.objects.create(
#         user=request.user,
#         restaurant=cart_items.first().menu_item.restaurant,
#         total_price=total_price
#     )

#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             menu_item=item.menu_item,
#             quantity=item.quantity,
#             price_at_order=item.menu_item.price
#         )

#     # cart khali kar do
#     cart_items.delete()

#     return redirect('order_confirmation', order_id=order.id)





from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def place_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'})
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'message': 'Please login to place an order',
            'redirect_url': reverse('users:login_signup')
        })
    
    # Check if user is a customer
    if request.user.role != 'customer':
        return JsonResponse({
            'success': False, 
            'message': 'Only customers can place orders'
        })
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        restaurant_id = data.get('restaurant_id')
        items = data.get('items', [])
        total = data.get('total', 0)
        
        # Validate data
        if not restaurant_id or not items:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid order data'
            })
        
        # Get restaurant
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        # ✅ Fix: Use correct field names from your Order model
        order = Order.objects.create(
            user=request.user,              # Changed from 'customer' to 'user'
            restaurant=restaurant,
            total_price=total,              # Changed from 'total_amount' to 'total_price'
            status='pending'
        )
        
        # Create order items
        for item_data in items:
            menu_item = get_object_or_404(MenuItem, id=item_data['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                price_at_order=item_data.get('price_at_order', menu_item.price)        # Make sure this matches your OrderItem model
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully!',
            'order_id': order.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error placing order: {str(e)}'
        })


# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from .models import Restaurant, MenuItem, Order, OrderItem
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @csrf_exempt
# def place_order(request):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'message': 'Method not allowed'})
    
#     # Check if user is authenticated
#     if not request.user.is_authenticated:
#         return JsonResponse({
#             'success': False, 
#             'message': 'Please login to place an order',
#             'redirect_url': reverse('users:login_signup')
#         })
    
#     # Check if user is a customer
#     if request.user.role != 'customer':
#         return JsonResponse({
#             'success': False, 
#             'message': 'Only customers can place orders'
#         })
    
#     try:
#         # Parse JSON data
#         data = json.loads(request.body)
#         restaurant_id = data.get('restaurant_id')
#         items = data.get('items', [])
#         total = data.get('total', 0)
        
#         # Validate data
#         if not restaurant_id or not items:
#             return JsonResponse({
#                 'success': False, 
#                 'message': 'Invalid order data'
#             })
        
#         # Get restaurant
#         restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
#         # Create order
#         order = Order.objects.create(
#             customer=request.user,
#             restaurant=restaurant,
#             total_amount=total,
#             status='pending'  # You can set appropriate status
#         )
        
#         # Create order items
#         for item_data in items:
#             menu_item = get_object_or_404(MenuItem, id=item_data['id'])
#             OrderItem.objects.create(
#                 order=order,
#                 menu_item=menu_item,
#                 quantity=item_data['quantity'],
#                 price=item_data['price']
#             )
        
#         return JsonResponse({
#             'success': True,
#             'message': 'Order placed successfully!',
#             'order_id': order.id
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': f'Error placing order: {str(e)}'
#         })




# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from .models import Order, OrderItem, MenuItem, Restaurant
# import json

# @login_required
# @require_POST
# def place_order(request):
#     try:
#         data = json.loads(request.body or '{}')
#         restaurant_id = data.get('restaurant_id')
#         items = data.get('items', [])
#         total_price = data.get('total', 0)

#         # Validate restaurant
#         restaurant = Restaurant.objects.get(pk=restaurant_id)

#         # Order create karo
#         order = Order.objects.create(
#             user=request.user,
#             restaurant=restaurant,
#             total_price=total_price,
#             status='pending'
#         )

#         # Items add karo
#         for item_data in items:
#             menu_item_id = item_data.get('id')
#             quantity = item_data.get('quantity', 1)
#             if not menu_item_id or quantity < 1:
#                 continue
#             menu_item = MenuItem.objects.get(pk=menu_item_id)
#             OrderItem.objects.create(
#                 order=order,
#                 menu_item=menu_item,
#                 quantity=quantity,
#                 price_at_order=menu_item.price
#             )

#         return JsonResponse({'success': True, 'order_id': order.id})

#     except Restaurant.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Restaurant not found'}, status=404)
#     except MenuItem.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Menu item not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)}, status=400)


# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse
# from .models import Restaurant, TableBooking
# from .forms import TableBookingForm


# @login_required(login_url="/accounts/login/")   # 👈 अगर user logged-in नहीं है → login पर redirect
# def book_table_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)

#     # पता करो किस URL से आया है
#     current_url = request.resolver_match.view_name  

#     if request.method == "POST":
#         form = TableBookingForm(request.POST)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.restaurant = restaurant
#             booking.user = request.user   # ✅ हमेशा logged-in user assign होगा
#             booking.save()
#             messages.success(request, "Booking request sent ✅")

#             # अलग-अलग जगह से आए तो अलग redirect
#             if current_url == "book_table_index":
#                 return redirect("home")
#             elif current_url == "book_table_cuisine":
#                 return redirect("spots_home")
#             else:
#                 # Default → confirmation page
#                 return redirect("restaurants:table_booking_confirmation", booking_id=booking.id)
#     else:
#         form = TableBookingForm()

#     return render(request, "users/user_side/table_booking_confirmation.html", {
#         "restaurant": restaurant,
#         "form": form,
#     })

from django.http import JsonResponse
from django.urls import reverse

@login_required(login_url="/accounts/login/")
def book_table_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)

    if request.method == "POST":
        form = TableBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.restaurant = restaurant
            booking.user = request.user
            booking.save()

            # agar AJAX request hai
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "message": "Booking request sent ✅",
                    "redirect_url": reverse("restaurants:table_booking_confirmation", args=[booking.id])
                })

            # agar normal request hoti (AJAX nahi hota)
            return redirect("restaurants:table_booking_confirmation", booking_id=booking.id)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": "Invalid form data"})
    else:
        form = TableBookingForm()

    return render(request, "users/user_side/table_booking_confirmation.html", {
        "restaurant": restaurant,
        "form": form,
    })



@login_required(login_url="/accounts/login/")   # 👈 confirmation page भी सिर्फ logged-in देख सके
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id, user=request.user)
    return render(request, "users/user_side/table_booking_confirmation.html", {"booking": booking})



# from django.urls import reverse

# def book_table_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)

#     # Determine where the request came from (URL name)
#     current_url = request.resolver_match.view_name

#     if request.method == 'POST':
#         form = TableBookingForm(request.POST)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.restaurant = restaurant
#             if request.user.is_authenticated:
#                 booking.user = request.user
#             booking.save()
#             messages.success(request, "Booking request sent ✅")

#             # Redirect based on the route used
#             if current_url == 'book_table_index':
#                 return redirect('home')  # or a dedicated success page for index
#             elif current_url == 'book_table_cuisine':
#                 return redirect('spots_home')  # or the spots/<slug> page
#     else:
#         form = TableBookingForm()

#     return render(request, 'spots/book_table.html', {
#         'restaurant': restaurant,
#         'form': form,
#     })



from django.core.mail import send_mail
def send_confirmation_email(booking):
    body = (
        f"Restaurant: {booking.restaurant.name}\n"
        f"Name: {booking.name or booking.user.get_full_name()}\n"
        f"Date: {booking.date}  Time: {booking.time}\n"
        f"Guests: {booking.no_of_guests}\n"
        f"Message: {booking.message}"
    )
    send_mail(
        subject="New table booking request",
        message=body,
        from_email="no-reply@zaykazone.com",
        recipient_list=["owner@zaykazone.com"],
        fail_silently=True,
    )

    
from itertools import islice
from django.utils import timezone
from django.db.models import Prefetch
from .models import Restaurant, MenuCategory, MenuItem
from django.db.models import Q # For complex queries if needed
from restaurants.models import Review
from django.db.models import Avg, Count

def restaurant_detail(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)

    # Get all images for this restaurant
    # all_images = RestaurantImage.objects.filter(restaurant=restaurant)
    all_images=restaurant.images.all()
    
    print(all_images)

    # Get the latest 4 images for the gallery preview (right-side section)
    # preview_images = all_images.order_by('-uploaded_at')[:4]
    # preview_qs = list(all_images.filter(is_preview=True).order_by('-uploaded_at'))
    # if not preview_qs:
    #         preview_qs = list(all_images.order_by('-uploaded_at'))
        
    # preview_images = list(islice(preview_qs, 4))
    # Manually filter preview images (no queryset operations)
    preview_qs = [img for img in all_images if img.is_preview]

    # Fallback: if no is_preview marked, use latest by uploaded_at manually
    if not preview_qs:
        preview_qs = sorted(all_images, key=lambda x: x.uploaded_at or timezone.now(), reverse=True)

    preview_images = list(islice(preview_qs, 4))  # final safe 4 preview images

    # Filter category-wise for full gallery filtering counts
    food_images = all_images.filter(category='food')
    ambience_images = all_images.filter(category='ambience')
    
    # menu categorys and menu items data
    menu_data = []
    # Get all menu categories related to this specific restaurant
    # You might also want to include global categories if applicable
    categories = MenuCategory.objects.filter(Q(restaurant=restaurant) | Q(is_global=True)).order_by('name')

    for category in categories:
        # Get all active menu items for the current category and restaurant
        items = MenuItem.objects.filter(
            restaurant=restaurant,
            category=category,
            is_available=True
        ).order_by('name')

        # Only add categories that have at least one item, or always add if you want empty categories displayed
        if items.exists(): # or if True to always include category even if empty
            menu_data.append({
                'category': category,
                'items': items,
            })

    reviews = Review.objects.filter(restaurant=restaurant)
    rating_stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))

    context = {
        'restaurant': restaurant,
        'images': all_images,  # for full gallery
        'preview_images': preview_images,  # for the 4-image preview section
        'food_images': food_images,        # optional if you're categorizing in template
        'ambience_images': ambience_images,
        'food_count': food_images.count(),
        'ambience_count': ambience_images.count(),
        'menu_data': menu_data,
        'reviews': reviews,
        'avg_rating': round(rating_stats['avg_rating'] or 0, 1),
        'total_reviews': rating_stats['total'],
    }
    return render(request, 'users/user_side/pepito.html', context)



from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from datetime import datetime
import json

@require_POST
def submit_review(request, slug):
    """Handle review submission via AJAX"""
    
    if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False, 
            "message": "You must be logged in to submit a review."
        }, status=401)
    
    try:
        # Get restaurant
        restaurant = get_object_or_404(Restaurant, slug=slug)
        
        # Extract data from POST request
        data = request.POST
        visit_date = data.get("visit_date")
        visit_type = data.get("visit_type")
        rating = data.get("rating")
        food_quality = data.get("food_quality")
        service_quality = data.get("service_quality")
        comment = data.get("comment")
        
        # Validate required fields
        required_fields = {
            'visit_date': visit_date,
            'visit_type': visit_type,
            'rating': rating,
            'food_quality': food_quality,
            'service_quality': service_quality,
            'comment': comment
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return JsonResponse({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)
        
        # Validate rating values
        try:
            rating = int(rating)
            food_quality = int(food_quality)
            service_quality = int(service_quality)
            
            for r in [rating, food_quality, service_quality]:
                if r < 1 or r > 5:
                    raise ValueError("Rating must be between 1 and 5")
                    
        except (ValueError, TypeError):
            return JsonResponse({
                "success": False,
                "message": "Invalid rating values. Please select ratings between 1 and 5."
            }, status=400)
        
        # Parse visit date
        try:
            visit_date = datetime.strptime(visit_date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({
                "success": False,
                "message": "Invalid date format."
            }, status=400)
        
        # Check if user already reviewed this restaurant on this date
        existing_review = Review.objects.filter(
            restaurant=restaurant,
            user=request.user,
            visit_date=visit_date
        ).first()
        
        if existing_review:
            return JsonResponse({
                "success": False,
                "message": "You have already reviewed this restaurant for this visit date."
            }, status=400)
        
        # Create the review
        review = Review.objects.create(
            restaurant=restaurant,
            user=request.user,
            visit_date=visit_date,
            visit_type=visit_type,
            rating=rating,
            food_quality=food_quality,
            service_quality=service_quality,
            comment=comment.strip(),
        )
        
        # Generate HTML for the new review
        html = render_to_string("partials/single_review.html", {
            "review": review,
            "request": request
        })
        
        return JsonResponse({
            "success": True,
            "html": html,
            "message": "Review submitted successfully!"
        })
        
    except ValidationError as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)
        
    except Exception as e:
        # Log the error in production
        print(f"Error submitting review: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "An error occurred while submitting your review. Please try again."
        }, status=500)
        
        
# from django.http import JsonResponse
# from django.template.loader import render_to_string

# def submit_review(request, slug):
#     if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
#         restaurant = get_object_or_404(Restaurant, slug=slug)
#         data = request.POST

#         review = Review.objects.create(
#             restaurant=restaurant,
#             user_name=request.user.username if request.user.is_authenticated else "Anonymous",
#             visit_date=data.get("visit_date"),
#             visit_type=data.get("visit_type"),
#             rating=data.get("rating"),
#             food_quality=data.get("food_quality"),
#             service_quality=data.get("service_quality"),
#             comment=data.get("comment"),
#         )

#         html = render_to_string("partials/single_review.html", {"review": review})
#         return JsonResponse({"success": True, "html": html})

#     return JsonResponse({"success": False}, status=400)


# def review_page(request):
#     restaurants = Restaurant.objects.all()
    
#     if request.method == "POST":
#         restaurant_id = request.POST.get("restaurant")
#         user_name = request.POST.get("user")
#         rating = request.POST.get("rating")
#         comment = request.POST.get("comment")

#         if restaurant_id and user_name and rating:
#             Review.objects.create(
#                 restaurant_id=restaurant_id,
#                 user_name=user_name,
#                 rating=rating,
#                 comment=comment
#             )
#             messages.success(request, "Thank you for your review!")
#             return redirect("your-review-page")
    
#     return render(request, "your_template.html", {"restaurants": restaurants})


# @login_required
# def order_view(request):
#     restaurant = Restaurant.objects.filter(owner=request.user).first()

#     if not restaurant:
#         messages.warning(request, "Pehle restaurant profile complete karo.")
#         return redirect("restaurants:restaurant_profile_settings")

#     menu_categories = MenuCategory.objects.filter(
#         restaurant=restaurant,
#         is_active=True
#     ).prefetch_related(
#         Prefetch(
#             'menuitem_set',
#             queryset=MenuItem.objects.filter(
#                 restaurant=restaurant,
#                 is_available=True
#             ),
#             to_attr='available_items'
#         )
#     ).order_by('name')

#     context = {
#         'menu_categories': menu_categories
#     }

#     return render(request, 'restaurants/admins/orders.html', context)


# def trending_spots_view(request):
#     # restaurants = Restaurant.objects.all().prefetch_related('images')
#     restaurants = Restaurant.objects.filter(approved=True)
#     restaurant_data = []
#     for restaurant in restaurants:
#         # preview_image = restaurant.images.filter(is_preview=True).first()
#         preview_image = restaurant.images.filter(category='food').first()
#         restaurant_data.append({
#             'restaurant': restaurant,
#             'preview_image': preview_image.image.url if preview_image else None
#         })

#     return render(request, 'users/user_side/spots.html', {
#         'restaurant_data': restaurant_data
#     })

# def trending_spots(request):
#     data = []
#     restaurants = Restaurant.objects.filter(approved=True)

#     for restaurant in restaurants:
#         image_obj = restaurant.images.filter(category='food').first()
#         image_url = image_obj.image.url if image_obj and image_obj.image else None

#         data.append({
#             'restaurant': restaurant,
#             'preview_image': image_url
#         })

#     return render(request, 'users/user_side/spots.html', {
#         'restaurant_data': data
#     })


# def trending_spots(request):
#     data = []
    
#     # Filter restaurants that are approved and have at least one cuisine named 'spots' (case-insensitive)
#     restaurants = Restaurant.objects.filter(
#         approved=True,
#         cuisines__name__iexact='spots'
#     ).distinct()

#     for restaurant in restaurants:
#         image_obj = restaurant.images.filter(category='food').first()
#         image_url = image_obj.image.url if image_obj and image_obj.image else None

#         data.append({
#             'restaurant': restaurant,
#             'preview_image': image_url
#         })

#     return render(request, 'users/user_side/spots.html', {
#         'restaurant_data': data
#     })


# Fetch only restaurants with cuisine containing 'spots'
# def trending_spots(request):
#     restaurants = (
#         Restaurant.objects.filter(cuisine__icontains='Spots',is_approved=True)
#         .prefetch_related('images')  # assuming related_name='images'
#     )

#     # Prepare data with 1 preview image
#     restaurant_data = []
#     for restaurant in restaurants:
#         preview_image = (
#             restaurant.images.first().image.url
#             if restaurant.images.exists()
#             else '/static/users/assets/img/about.jpg'
#         )

#         restaurant_data.append({
#             'restaurant': restaurant,
#             'preview_image': preview_image,
#         })

#     return render(request, 'users/user_side/spots.html', {'restaurant_data': restaurant_data})


def cuisine_page(request, slug):
    # Page content for heading, description, background
    # page_content = get_object_or_404(CuisinePageContent, cuisine_name__iexact=cuisine)
    page_content = get_object_or_404(CuisinePageContent, slug=slug)
    
    cuisine = page_content.cuisine_name
    
    # Approved restaurants with matching cuisine
    restaurants = (
        Restaurant.objects.filter(cuisine__icontains=cuisine, is_approved=True)
        .prefetch_related('images')
    )

    restaurant_data = []
    for restaurant in restaurants:
        preview_image = (
            restaurant.images.first().image.url
            if restaurant.images.exists()
            else '/static/users/assets/img/about.jpg'
        )

        restaurant_data.append({
            'restaurant': restaurant,
            'preview_image': preview_image,
        })

    return render(request, 'users/user_side/spots.html', {
        'restaurant_data': restaurant_data,
        'page_content': page_content,
        'cuisine_name': cuisine,
    })


@login_required
def restaurant_create_view(request):
    """
    Owner onboarding - ek hi page par Restaurant + OwnerProfile (GST आदि) भरते हैं.
    """

    # ⬇️ OwnerProfile हमेशा मिल जाएगा, वरना बन जाएगा
    owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
      r_form = RestaurantForm(request.POST, request.FILES)
      o_form = OwnerProfileForm(request.POST, instance=owner_profile)

      if r_form.is_valid() and o_form.is_valid():
        # Restaurant object create
        restaurant = r_form.save(commit=False)
        restaurant.owner = request.user
        restaurant.is_approved = False  # ✅ Approval pending
        # Auto city/cuisine
        description = r_form.cleaned_data.get("description", "")
        address     = r_form.cleaned_data.get("address", "")
        if not restaurant.cuisine:
            restaurant.cuisine = extract_from_text(description, CUISINES)
        if not restaurant.city:
            restaurant.city = extract_from_text(address, CITIES)
        restaurant.save()

        # OwnerProfile object create
        owner_profile = o_form.save(commit=False)
        owner_profile.user = request.user
        owner_profile.restaurant = restaurant
        owner_profile.save()

        messages.success(request, "Aapki request admin ke paas chali gayi hai. Approval ke baad aapka dashboard khulega.")
        return redirect("restaurants:restaurant_profile_settings")

      messages.error(request, "Form me kuch error hai. Kripya check karo.")

    else:
       r_form = RestaurantForm()
       o_form = OwnerProfileForm(instance=owner_profile)

    return render(request, "restaurants/admins/profile_settings.html", {
    "r_form": r_form,
    "o_form": o_form,
    })




# @login_required
# def restaurant_create_view(request):
#     """Owner onboarding - एक ही पेज पर Restaurant + Owner GST details."""
#     # ⬇️ GET या POST दोनों के लिए: मौजूदा OwnerProfile object
#     owner_profile, _ = RestaurantOwnerProfile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         r_form  = RestaurantForm(request.POST, request.FILES)
#         o_form  = OwnerProfileForm(request.POST, instance=owner_profile)

#         # दोनों form valid?
#         if r_form.is_valid() and o_form.is_valid():
#             # -------- Restaurant save --------
#             restaurant = r_form.save(commit=False)
#             restaurant.owner = request.user

#             # cleaned_data se description / address उठा लो
#             description = r_form.cleaned_data['description']
#             address     = r_form.cleaned_data['address']

#             # auto city / cuisine
#             if not restaurant.cuisine:
#                 restaurant.cuisine = extract_from_text(description, CUISINES)
#             if not restaurant.city:
#                 restaurant.city = extract_from_text(address, CITIES)

#             restaurant.save()                     # slug logic runs here

#             # -------- Owner profile save (GST, etc.) --------
#             o_form.save()

#             return redirect('restaurants:dashboard')   # सफलता के बाद
#     else:
#         r_form = RestaurantForm()
#         o_form = OwnerProfileForm(instance=owner_profile)

#     context = {'r_form': r_form, 'o_form': o_form}
#     return render(request, 'restaurants/admins/profile_settings.html', context)

# def restaurant_create_view(request):
#     if request.method == 'POST':
#         form = RestaurantForm(request.POST, request.FILES)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.owner = request.user
#             if not restaurant.cuisine:
#                 restaurant.cuisine = extract_from_text(restaurant.description, CUISINES)
#             if not restaurant.city:
#                 restaurant.city = extract_from_text(restaurant.address, CITIES)
#             restaurant.save()
#             return redirect('restaurants:dashboard')
#     else:
#         form = RestaurantForm()
    
#     return render(request, 'restaurants/admins/profile_settings.html', {'form': form})


