from django.shortcuts import render,redirect, get_object_or_404

from .models import Restaurant,Review,RestaurantImage,CartItem,RestaurantUserVisit     # Restaurant model
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


# @login_required
# def dashboard_view(request, slug):
#     # Get restaurant with security checks
#     restaurant = get_object_or_404(
#         Restaurant, 
#         slug=slug, 
#         # owner=request.user,
#         # owner_name__iexact=request.user,  # Case-insensitive match
#         owner=request.user,
#         is_approved=True
#     )
    
#     # Get approval status
#     approval_request = RestaurantApprovalRequest.objects.filter(
#         restaurant=restaurant
#     ).first()
    
#     # Get menu data
#     menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
#     menu_items = MenuItem.objects.filter(restaurant=restaurant)
    
#     # Get bookings (today and upcoming)
#     today = timezone.now().date()
#     upcoming_bookings = TableBooking.objects.filter(
#         restaurant=restaurant,
#         date__gte=today,
#         status__in=['pending', 'confirmed']
#     ).order_by('date', 'time')[:5]
    
#     # Get recent reviews
#     recent_reviews = Review.objects.filter(
#         restaurant=restaurant
#     ).order_by('-created_at')[:5]
    
#     # Get recent orders (last 7 days)
#     one_week_ago = timezone.now() - timedelta(days=7)
#     recent_orders = Order.objects.filter(
#         restaurant=restaurant,
#         timestamp__gte=one_week_ago
#     ).order_by('-timestamp')[:10]
    
#     # Get preview images
#     preview_images = RestaurantImage.objects.filter(
#         restaurant=restaurant,
#         is_preview=True
#     )[:4]
    
#     # Calculate pending orders count
#     pending_orders_count = Order.objects.filter(
#         restaurant=restaurant,
#         status__in=['pending', 'confirmed', 'preparing']
#     ).count()
    
#     # Get owner profile
#     try:
#         owner_profiles = request.user.owner_profiles
#     except RestaurantOwnerProfile.DoesNotExist:
#         owner_profiles = None
    
#     # Get cart items count for user
#     cart_items_count = CartItem.objects.filter(user=request.user).count()
    
#     # Get all user's restaurants for switcher
#     user_restaurants = Restaurant.objects.filter(
#         owner=request.user,
#         is_approved=True
#     ).exclude(id=restaurant.id) #current ko hatao
    
#     context = {
#         'owner_profile': owner_profiles,
#         'restaurant': restaurant, # current restaurant
#         'user_restaurants': user_restaurants,  # dropdown ke liye sirf current
#         'approval_request': approval_request,
#         'menu_categories_count': menu_categories.count(),
#         'menu_items_count': menu_items.count(),
#         'upcoming_bookings': upcoming_bookings,
#         'upcoming_bookings_count': upcoming_bookings.count(),
#         'recent_reviews': recent_reviews,
#         'recent_reviews_count': recent_reviews.count(),
#         'recent_orders': recent_orders,
#         'recent_orders_count': recent_orders.count(),
#         'preview_images': preview_images,
#         'pending_orders_count': pending_orders_count,
#         'cart_items_count': cart_items_count,
#         'user_restaurants': user_restaurants,
#     }
    
#     return render(request, 'restaurants/admins/dashboard.html', context)


# @login_required
# def dashboard_view(request, slug):
#     # Get restaurant with security checks
#     restaurant = get_object_or_404(
#         Restaurant, 
#         slug=slug, 
#         owner=request.user,
#         is_approved=True
#     )
    
#     # Get approval status
#     approval_request = RestaurantApprovalRequest.objects.filter(
#         restaurant=restaurant
#     ).first()
    
#     # Get menu data
#     menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
#     menu_items = MenuItem.objects.filter(restaurant=restaurant)
    
#     # Get bookings (today and upcoming)
#     today = timezone.now().date()
#     upcoming_bookings = TableBooking.objects.filter(
#         restaurant=restaurant,
#         date__gte=today,
#         status__in=['pending', 'confirmed']
#     ).order_by('date', 'time')[:5]
    
#     # Get recent reviews
#     recent_reviews = Review.objects.filter(
#         restaurant=restaurant
#     ).order_by('-created_at')[:5]
    
#     # Get recent orders (last 7 days)
#     one_week_ago = timezone.now() - timedelta(days=7)
#     recent_orders = Order.objects.filter(
#         restaurant=restaurant,
#         timestamp__gte=one_week_ago
#     ).order_by('-timestamp')[:10]
    
#     # Get preview images
#     preview_images = RestaurantImage.objects.filter(
#         restaurant=restaurant,
#         is_preview=True
#     )[:4]
    
#     # Calculate pending orders count
#     pending_orders_count = Order.objects.filter(
#         restaurant=restaurant,
#         status__in=['pending', 'confirmed', 'preparing']
#     ).count()
    
#     # NEW: Calculate total users/customers
#     total_users = User.objects.filter(
#         order__restaurant=restaurant
#     ).distinct().count()
    
#     # FIXED: Use total_price instead of total_amount
#     revenue = Order.objects.filter(
#         restaurant=restaurant,
#         status='delivered'  # Changed from 'completed' to 'delivered' as per your model
#     ).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
    
#     # NEW: Calculate total orders count
#     orders_count = Order.objects.filter(restaurant=restaurant).count()
    
#     # NEW: Calculate total reviews count
#     reviews_count = Review.objects.filter(restaurant=restaurant).count()
    
#     # NEW: Get top products (most ordered)
#     top_products = MenuItem.objects.filter(
#         restaurant=restaurant
#     ).annotate(
#         total_ordered=Count('orderitem')
#     ).order_by('-total_ordered')[:5]
    
#     # NEW: Create activities from recent events
#     activities = []
    
#     # Add recent orders as activities
#     for order in recent_orders[:3]:
#         activities.append({
#             'user': order.user,
#             'message': f'New order placed',
#             'details': f'Order #{order.id} - ₹{order.total_price}',  # FIXED: total_price
#             'time': order.timestamp
#         })
    
#     # Add recent reviews as activities
#     for review in recent_reviews[:2]:
#         activities.append({
#             'user': review.user,
#             'message': f'New review received',
#             'details': f'Rating: {review.rating}/5',
#             'time': review.created_at
#         })
    
#     # Add recent bookings as activities
#     for booking in upcoming_bookings[:2]:
#         activities.append({
#             'user': booking.user,
#             'message': f'Table booking made',
#             'details': f'For {booking.no_of_guests} people on {booking.date}',  # FIXED: no_of_guests
#             'time': booking.created_at
#         })
    
#     # Sort activities by time (newest first)
#     activities.sort(key=lambda x: x['time'], reverse=True)
    
#     # Get owner profile
#     try:
#         owner_profiles = request.user.owner_profiles
#     except RestaurantOwnerProfile.DoesNotExist:
#         owner_profiles = None
    
#     # Get cart items count for user
#     cart_items_count = CartItem.objects.filter(user=request.user).count()
    
#     # Get all user's restaurants for switcher
#     user_restaurants = Restaurant.objects.filter(
#         owner=request.user,
#         is_approved=True
#     ).exclude(id=restaurant.id)
    
#     context = {
#         'owner_profile': owner_profiles,
#         'restaurant': restaurant,
#         'user_restaurants': user_restaurants,
#         'approval_request': approval_request,
#         'menu_categories_count': menu_categories.count(),
#         'menu_items_count': menu_items.count(),
#         'upcoming_bookings': upcoming_bookings,
#         'upcoming_bookings_count': upcoming_bookings.count(),
#         'recent_reviews': recent_reviews,
#         'recent_reviews_count': recent_reviews.count(),
#         'recent_orders': recent_orders,
#         'recent_orders_count': recent_orders.count(),
#         'preview_images': preview_images,
#         'pending_orders_count': pending_orders_count,
#         'cart_items_count': cart_items_count,
        
#         # NEW VARIABLES ADDED
#         'total_users': total_users,
#         'revenue': revenue,
#         'orders_count': orders_count,
#         'reviews_count': reviews_count,
#         'activities': activities,
#         'top_products': top_products,
#     }
    
#     return render(request, 'restaurants/admins/dashboard.html', context)


# Updated views.py (assuming this is in your restaurants/views.py or similar)
# I've included the original two views and added the new search_suggestions view.
# Make sure to add all necessary imports at the top.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from datetime import timedelta, date
from .models import Restaurant, RestaurantApprovalRequest, MenuCategory, MenuItem, TableBooking, Review, Order, RestaurantImage, RestaurantOwnerProfile, CartItem, User
import json 

@login_required
def dashboard_view(request, slug):
    # Get restaurant with security checks
    restaurant = get_object_or_404(
        Restaurant, 
        slug=slug, 
        owner=request.user,
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
    
    # Calculate total users/customers (unique from orders and bookings)
    order_users = User.objects.filter(order__restaurant=restaurant).distinct()
    booking_users = User.objects.filter(tablebooking__restaurant=restaurant).distinct()
    total_users = order_users.union(booking_users).count()
    
    # Revenue calculations - FIXED: Use total_amount instead of amount
    order_revenue = Order.objects.filter(
        restaurant=restaurant,
        status='delivered'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    booking_revenue = TableBooking.objects.filter(
        restaurant=restaurant,
        status='confirmed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0  # FIXED: amount -> total_amount
    
    # Total revenue (both orders and bookings)
    total_revenue = order_revenue + booking_revenue
    
    # Transaction counts
    orders_count = Order.objects.filter(restaurant=restaurant).count()
    bookings_count = TableBooking.objects.filter(restaurant=restaurant).count()
    total_transactions = orders_count + bookings_count
    
    # Reviews count
    reviews_count = Review.objects.filter(restaurant=restaurant).count()
    
    # Pending counts
    pending_orders_count = Order.objects.filter(
        restaurant=restaurant,
        status__in=['pending', 'confirmed', 'preparing']
    ).count()
    
    pending_bookings_count = TableBooking.objects.filter(
        restaurant=restaurant,
        status='pending'
    ).count()
    
    pending_count = pending_orders_count + pending_bookings_count
    
    # Get top products
    top_products = MenuItem.objects.filter(
        restaurant=restaurant
    ).annotate(
        total_ordered=Count('orderitem')
    ).order_by('-total_ordered')[:5]
    
    # Create activities from recent events
    activities = []
    
    # Add recent orders as activities
    for order in recent_orders[:3]:
        activities.append({
            'type': 'order',
            'user': order.user,
            'message': f'New order placed',
            'details': f'Order #{order.id} - ₹{order.total_price}',
            'time': order.timestamp,
            'status': order.status
        })
    
    # Add recent reviews as activities
    for review in recent_reviews[:2]:
        activities.append({
            'type': 'review',
            'user': review.user,
            'message': f'New review received',
            'details': f'Rating: {review.rating}/5',
            'time': review.created_at,
            'rating': review.rating
        })
    
    # Add recent bookings as activities
    for booking in upcoming_bookings[:2]:
        activities.append({
            'type': 'booking',
            'user': booking.user,
            'message': f'Table booking made',
            'details': f'For {booking.no_of_guests} people on {booking.date}',
            'time': booking.created_at,
            'status': booking.status
        })
    
    # Sort activities by time (newest first)
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    # Get owner profile
    try:
        owner_profiles = request.user.owner_profiles
    except RestaurantOwnerProfile.DoesNotExist:
        owner_profiles = None
    
    # Get cart items count for user
    cart_items_count = CartItem.objects.filter(user=request.user).count()
    
    # Get all user's restaurants for switcher
    user_restaurants = Restaurant.objects.filter(
        owner=request.user,
        is_approved=True
    ).exclude(id=restaurant.id)
    
    # Revenue data for charts (Orders + Bookings) - FIXED: Use total_amount
    def compute_revenue_data(days, trunc_func, date_format):
        start_date = timezone.now().date() - timedelta(days=days - 1)
        end_date = timezone.now().date()
        
        # Orders revenue
        orders_data = Order.objects.filter(
            restaurant=restaurant,
            status='delivered',
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).annotate(
            period=trunc_func('timestamp')
        ).values('period').annotate(
            total=Sum('total_price')
        ).order_by('period')
        
        # Bookings revenue - FIXED: amount -> total_amount
        bookings_data = TableBooking.objects.filter(
            restaurant=restaurant,
            status='confirmed',
            date__gte=start_date,
            date__lte=end_date
        ).annotate(
            period=trunc_func('date')
        ).values('period').annotate(
            total=Sum('total_amount')  # FIXED: amount -> total_amount
        ).order_by('period')
        
        # Combine data using period as date key
        combined = {}
        for item in orders_data:
            period_date = item['period'].date() if isinstance(item['period'], datetime) else item['period']
            if period_date not in combined:
                combined[period_date] = {'orders': 0, 'bookings': 0, 'total': 0}
            combined[period_date]['orders'] = float(item['total'] or 0)
            combined[period_date]['total'] += float(item['total'] or 0)
        
        for item in bookings_data:
            period_date = item['period'].date() if isinstance(item['period'], datetime) else item['period']
            if period_date not in combined:
                combined[period_date] = {'orders': 0, 'bookings': 0, 'total': 0}
            combined[period_date]['bookings'] = float(item['total'] or 0)
            combined[period_date]['total'] += float(item['total'] or 0)
        
        # Generate complete list of periods
        labels = []
        orders_revenue = []
        bookings_revenue = []
        total_revenue = []
        
        if trunc_func == TruncDay:
            current_period = start_date
            delta = timedelta(days=1)
            label_func = lambda d: d.strftime(date_format)
            key_func = lambda d: d
        elif trunc_func == TruncWeek:
            current_period = start_date - timedelta(days=start_date.weekday())
            delta = timedelta(days=7)
            label_func = lambda d: f'Week starting {d.strftime("%b %d")}'
            key_func = lambda d: d
        elif trunc_func == TruncMonth:
            current_period = start_date.replace(day=1)
            delta = None
            label_func = lambda d: d.strftime('%b %Y')
            key_func = lambda d: d
        
        while current_period <= end_date:
            period_key = key_func(current_period)
            label = label_func(current_period)
            data_point = combined.get(period_key, {'orders': 0, 'bookings': 0, 'total': 0})
            
            labels.append(label)
            orders_revenue.append(data_point['orders'])
            bookings_revenue.append(data_point['bookings'])
            total_revenue.append(data_point['total'])
            
            if delta:
                current_period += delta
            else:  # For months
                next_month = current_period.month + 1
                next_year = current_period.year + (next_month > 12)
                next_month = next_month if next_month <= 12 else 1
                current_period = current_period.replace(year=next_year, month=next_month)
        
        return {
            'labels': labels,
            'datasets': {
                'orders': orders_revenue,
                'bookings': bookings_revenue,
                'total': total_revenue
            }
        }
    
    # Generate revenue data for different periods
    revenue_data = {
        '7': compute_revenue_data(7, TruncDay, '%b %d'),
        '30': compute_revenue_data(30, TruncWeek, 'Week starting %b %d'),
        '90': compute_revenue_data(90, TruncMonth, '%b %Y'),
    }
    
    # Search suggestions data
    search_suggestions = {
        'orders': list(Order.objects.filter(restaurant=restaurant).values_list('id', flat=True)[:10]),
        'customers': list(User.objects.filter(
            Q(order__restaurant=restaurant) | Q(tablebooking__restaurant=restaurant)
        ).distinct().values_list('full_name', flat=True)[:10]),
        'menu_items': list(MenuItem.objects.filter(restaurant=restaurant).values_list('name', flat=True)[:10]),
    }
    
    context = {
        'owner_profile': owner_profiles,
        'restaurant': restaurant,
        'user_restaurants': user_restaurants,
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
        'cart_items_count': cart_items_count,
        
        # Revenue and metrics
        'total_users': total_users,
        'revenue': total_revenue,
        'order_revenue': order_revenue,
        'booking_revenue': booking_revenue,
        'orders_count': orders_count,
        'bookings_count': bookings_count,
        'total_transactions': total_transactions,
        'reviews_count': reviews_count,
        'activities': activities,
        'top_products': top_products,
        'pending_orders_count': pending_count,
        
        # Chart data
        'revenue_data_json': json.dumps(revenue_data),
        'search_suggestions_json': json.dumps(search_suggestions),
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

# def menu_view(request, slug):
#     # Get the restaurant based on the slug
#     restaurant = get_object_or_404(Restaurant, slug=slug)
    
#     # Get menu items and categories for this restaurant
#     menu_items = MenuItem.objects.filter(restaurant=restaurant)
#     categories = MenuCategory.objects.filter(restaurant=restaurant)
    
#     context = {
#         'restaurant': restaurant,
#         'menu_items': menu_items,
#         'categories': categories
#     }
#     return render(request, 'restaurants/admins/menus.html', context)

# from django.shortcuts import redirect
# from .forms import MenuCategoryCreateForm

# def add_category(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     if request.method == 'POST':
#         form = MenuCategoryCreateForm(request.POST)
#         if form.is_valid():
#             category = form.save(commit=False)
#             category.restaurant = restaurant
#             category.save()
#             return redirect('restaurants:menu', slug=restaurant.slug)
#     else:
#         form = MenuCategoryCreateForm()
    
#     return render(request, 'restaurants/admins/add_category.html', {
#         'form': form,
#         'restaurant': restaurant
#     })
    
# from .forms import MenuItemCreateForm

# def edit_menu_item(request, slug, item_id):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     menu_item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    
#     if request.method == 'POST':
#         form = MenuItemCreateForm(request.POST, request.FILES, instance=menu_item)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Menu item updated successfully!')
#             return redirect('restaurants:menu', slug=restaurant.slug)
#     else:
#         form = MenuItemCreateForm(instance=menu_item)
    
#     return render(request, 'restaurants/admins/edit_menu_item.html', {
#         'form': form,
#         'restaurant': restaurant,
#         'menu_item': menu_item
#     })

# def delete_menu_item(request, slug, item_id):
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Restaurant, MenuCategory, MenuItem
from .forms import MenuCategoryCreateForm, MenuItemCreateForm

def menu_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    categories = MenuCategory.objects.filter(restaurant=restaurant).prefetch_related("items")
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    return render(request, "restaurants/admins/menus.html", {
        "restaurant": restaurant,
        "categories": categories,
        "menu_items": menu_items,
    })


# ✅ Add Category
def add_category(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == "POST":
        form = MenuCategoryCreateForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect("restaurants:menu", slug=restaurant.slug)
    return redirect("restaurants:menu", slug=restaurant.slug)


# ✅ Delete Category
def delete_category(request, slug, category_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("restaurants:menu", slug=restaurant.slug)


# ✅ Add Menu Item
def add_menu_item(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == "POST":
        form = MenuItemCreateForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect("restaurants:menu", slug=restaurant.slug)
    return redirect("restaurants:menu", slug=restaurant.slug)


# ✅ Delete Menu Item
def delete_menu_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    item.delete()
    messages.success(request, "Menu item deleted successfully!")
    return redirect("restaurants:menu", slug=restaurant.slug)


# ✅ Edit Category
def edit_category(request, slug, category_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)

    if request.method == "POST":
        form = MenuCategoryCreateForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("restaurants:menu", slug=restaurant.slug)
    else:
        form = MenuCategoryCreateForm(instance=category)

    return render(request, "restaurants/admins/edit_category.html", {
        "restaurant": restaurant,
        "form": form,
        "category": category,
    })


# ✅ Edit Menu Item
def edit_menu_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)

    if request.method == "POST":
        form = MenuItemCreateForm(
            request.POST, 
            request.FILES, 
            instance=item,
            restaurant=restaurant,
            category=item.category   # 👈 यह ज़रूरी है
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully!")
            return redirect("restaurants:menu", slug=restaurant.slug)
    else:
        form = MenuItemCreateForm(
            instance=item,
            restaurant=restaurant,
            category=item.category   # 👈 यह ज़रूरी है
        )

    return render(request, "restaurants/admins/edit_item.html", {
        "restaurant": restaurant,
        "form": form,
        "item": item,
    })


    
# def order_view(request,slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     return render(request, 'restaurants/admins/orders.html', {'restaurant': restaurant})
# def order_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     orders = Order.objects.filter(restaurant=restaurant).select_related("user").prefetch_related("order_items__menu_item")

#     return render(request, 'restaurants/admins/orders.html', {
#         'restaurant': restaurant,
#         'orders': orders
#     })
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Restaurant, Order

def order_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    # latest first
    orders_list = (
        Order.objects.filter(restaurant=restaurant)
        #Filters Order rows to only those whose restaurant FK equals the restaurant you passed (that restaurant can be a Restaurant instance or an id).Result: a QuerySet of Order instances (lazy — no DB hit yet).
        .select_related("user")
        .prefetch_related("order_items__menu_item")
        #This is a nested prefetch. It tells Django to prefetch the reverse FK order_items (the OrderItem objects related to each Order) and for those OrderItems prefetch their menu_item FK.order_items is the related_name on OrderItem (so order.order_items.all()), and menu_item is its FK.
        .order_by("-timestamp")
    )
    #fetch all MenuItem rows whose ids are used by those OrderItems.
    # Then Django stitches the results in Python memory: it attaches the OrderItem instances to each Order and attaches each MenuItem to its OrderItem.

    # pagination (10 orders per page)
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)

    return render(request, "restaurants/admins/orders.html", {
        "restaurant": restaurant,
        "orders": orders
    })



# def table_view(request,slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     return render(request, 'restaurants/admins/tables.html', {'restaurant': restaurant})

def table_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)

    # Sirf iss restaurant ke bookings
    bookings = TableBooking.objects.filter(restaurant=restaurant).select_related("user")

    return render(request, 'restaurants/admins/tables.html', {
        'restaurant': restaurant,
        'bookings': bookings
    })

from django.shortcuts import render, get_object_or_404
from .models import Restaurant, Review

def feedback_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    # Saare reviews fetch karo is restaurant ke
    reviews = restaurant.reviews.all().order_by('-created_at')  
    
    # Agar aap priority ke hisaab se filter karna chaho
    high_priority = reviews.filter(priority="high")
    medium_priority = reviews.filter(priority="medium")
    low_priority = reviews.filter(priority="low")
    system_priority = reviews.filter(priority="system")
    
    return render(request, 'restaurants/admins/feedbacks.html', {
        'restaurant': restaurant,
        'reviews': reviews,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'system_priority': system_priority,
    })


# def users_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     return render(request, 'restaurants/admins/users.html', {'restaurant': restaurant})

# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth import get_user_model
# from .models import Restaurant, RestaurantUserVisit, Order

# User = get_user_model()

# def users_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)

#     # अगर login user है तो उसका visit record करो
#     if request.user.is_authenticated:
#         RestaurantUserVisit.objects.get_or_create(
#             restaurant=restaurant,
#             user=request.user
#         )

#     # Visit करने वाले users
#     visit_users = User.objects.filter(
#         restaurant_visits__restaurant=restaurant
#     )

#     # Order करने वाले users
#     order_users = User.objects.filter(
#         order__restaurant=restaurant
#     )

#     # Merge करके unique users list
#     users = (visit_users | order_users).distinct()

#     return render(request, 'restaurants/admins/users.html', {
#         'restaurant': restaurant,
#         'users': users
#     })


# from django.contrib.auth import get_user_model
# User = get_user_model()

#for distinct users
# def users_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)

#     if request.user.is_authenticated:
#         RestaurantUserVisit.objects.get_or_create(
#             restaurant=restaurant,
#             user=request.user
#         )

#     # visit karne wale users (admin/restaurant exclude)
#     visit_users = User.objects.filter(
#         restaurant_visits__restaurant=restaurant
#     ).exclude(role__in=["admin", "restaurant"]).distinct()

#     # order karne wale users
#     order_users = User.objects.filter(
#         order__restaurant=restaurant
#     ).exclude(role__in=["admin", "restaurant"]).distinct()

#     # table booking karne wale users
#     booking_users = User.objects.filter(
#         tablebooking__restaurant=restaurant
#     ).exclude(role__in=["admin", "restaurant"]).distinct()

#     users = []
#     for user in visit_users:
#         if user in order_users or user in booking_users:
#             role = "customer"
#         else:
#             role = "user"
#         users.append({
#             "user": user,
#             "role": role
#         })

#     # agar koi user sirf order/booking kare without visit
#     for user in (order_users | booking_users):
#         if not any(u["user"] == user for u in users):
#             users.append({
#                 "user": user,
#                 "role": "customer"
#             })

#     return render(request, 'restaurants/admins/users.html', {
#         "restaurant": restaurant,
#         "users": users
#     })



def users_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)

    if request.user.is_authenticated:
        RestaurantUserVisit.objects.create(
            restaurant=restaurant,
            user=request.user
        )

    users = []

    # 1. Visits
    for visit in RestaurantUserVisit.objects.filter(restaurant=restaurant).select_related("user"):
        if visit.user.role not in ["admin", "restaurant"]:
            users.append({
                "user": visit.user,
                "role": "user"
            })

    # 2. Orders
    for order in Order.objects.filter(restaurant=restaurant).select_related("user"):
        if order.user.role not in ["admin", "restaurant"]:
            users.append({
                "user": order.user,
                "role": "customer"
            })

    # 3. Table Bookings
    for booking in TableBooking.objects.filter(restaurant=restaurant).select_related("user"):
        if booking.user.role not in ["admin", "restaurant"]:
            users.append({
                "user": booking.user,
                "role": "customer"
            })

    return render(request, "restaurants/admins/users.html", {
        "restaurant": restaurant,
        "users": users
    })


def profile_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    
    if request.method == "POST":
        restaurant.name = request.POST.get("name", restaurant.name)
        restaurant.description = request.POST.get("description", restaurant.description)
        restaurant.address = request.POST.get("address", restaurant.address)
        restaurant.timings = request.POST.get("timings", restaurant.timings)
        if request.FILES.get("logo"):
            restaurant.logo = request.FILES["logo"]
        restaurant.save()
        return redirect("restaurants:profile", slug=restaurant.slug)

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
            
        # ✅ STEP 1: Save restaurant first
        restaurant.save()

        # Owner name logic
        updated_owner_name = request.POST.get("owner_name", "").strip()
        
        # ✅ Update owner_profile regardless
        owner_profile.full_name = updated_owner_name or user.full_name
        owner_profile.email = request.POST.get("owner_email", "").strip()
        owner_profile.phone = request.POST.get("owner_phone", "").strip()
        owner_profile.gst_number = request.POST.get("gst_number", "").strip()
        owner_profile.restaurant = restaurant
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

# from django.http import JsonResponse
# from django.urls import reverse

# @login_required(login_url="/accounts/login/")
# def book_table_view(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)

#     if request.method == "POST":
#         form = TableBookingForm(request.POST)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.restaurant = restaurant
#             booking.user = request.user
#             booking.save()
            
#             # Calculate amount (example: 100 per guest)
#             amount = booking.no_of_guests * 100  # Adjust as needed
            
#             # agar AJAX request hai
#             if request.headers.get("X-Requested-With") == "XMLHttpRequest":
#                 return JsonResponse({
#                     "success": True,
#                     "message": "Booking request sent ✅",
#                     "redirect_url": reverse("restaurants:table_booking_confirmation", args=[booking.id])
#                 })

#             # agar normal request hoti (AJAX nahi hota)
#             return redirect("restaurants:table_booking_confirmation", booking_id=booking.id)
#         else:
#             if request.headers.get("X-Requested-With") == "XMLHttpRequest":
#                 return JsonResponse({"success": False, "error": "Invalid form data"})
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
            
            table_price=booking.restaurant.table_booking_price

            # Calculate amount (example: 100 per guest)
            amount = booking.no_of_guests * table_price  # Adjust as needed

            # agar AJAX request hai
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "message": "Booking request sent ✅",
                    "booking_id": booking.id,
                    "amount": amount,
                    "redirect_url": reverse("restaurants:table_booking_confirmation", args=[booking.id])
                })

            # agar normal request hoti (AJAX nahi hota)
            return redirect("restaurants:table_booking_confirmation", booking_id=booking.id)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": form.errors.as_json()})
    else:
        form = TableBookingForm()

    return render(request, "users/user_side/table_booking_confirmation.html", {
        "restaurant": restaurant,
        "form": form,
    })

@login_required(login_url="/accounts/login/")   # 👈 confirmation page भी सिर्फ logged-in देख सके
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id, user=request.user)
    restaurant=booking.restaurant
    return render(request, "users/user_side/table_booking_confirmation.html", {"booking": booking,"restaurant":restaurant})



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

    
# from itertools import islice
# from django.utils import timezone
# from django.db.models import Prefetch
# from .models import Restaurant, MenuCategory, MenuItem
# from django.db.models import Q # For complex queries if needed
# from restaurants.models import Review
# from django.db.models import Avg, Count
# from django.views.decorators.csrf import ensure_csrf_cookie

# @ensure_csrf_cookie
# def restaurant_detail(request, slug):
#     restaurant = get_object_or_404(Restaurant, slug=slug)
#     # Get all images for this restaurant
#     # all_images = RestaurantImage.objects.filter(restaurant=restaurant)
#     all_images=restaurant.images.all()
    
#     print(all_images)

#     # Get the latest 4 images for the gallery preview (right-side section)
#     # preview_images = all_images.order_by('-uploaded_at')[:4]
#     # preview_qs = list(all_images.filter(is_preview=True).order_by('-uploaded_at'))
#     # if not preview_qs:
#     #         preview_qs = list(all_images.order_by('-uploaded_at'))
        
#     # preview_images = list(islice(preview_qs, 4))
#     # Manually filter preview images (no queryset operations)
#     preview_qs = [img for img in all_images if img.is_preview]

#     # Fallback: if no is_preview marked, use latest by uploaded_at manually
#     if not preview_qs:
#         preview_qs = sorted(all_images, key=lambda x: x.uploaded_at or timezone.now(), reverse=True)

#     preview_images = list(islice(preview_qs, 4))  # final safe 4 preview images

#     # Filter category-wise for full gallery filtering counts
#     food_images = all_images.filter(category='food')
#     ambience_images = all_images.filter(category='ambience')
    
#     # menu categorys and menu items data
#     menu_data = []
#     # Get all menu categories related to this specific restaurant
#     # You might also want to include global categories if applicable
#     categories = MenuCategory.objects.filter(Q(restaurant=restaurant) | Q(is_global=True)).order_by('name')

#     for category in categories:
#         # Get all active menu items for the current category and restaurant
#         items = MenuItem.objects.filter(
#             restaurant=restaurant,
#             category=category,
#             is_available=True
#         ).order_by('name')

#         # Only add categories that have at least one item, or always add if you want empty categories displayed
#         if items.exists(): # or if True to always include category even if empty
#             menu_data.append({
#                 'category': category,
#                 'items': items,
#             })

#     reviews = Review.objects.filter(restaurant=restaurant)
#     rating_stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))

#     context = {
#         'restaurant': restaurant,
#         'images': all_images,  # for full gallery
#         'preview_images': preview_images,  # for the 4-image preview section
#         'food_images': food_images,        # optional if you're categorizing in template
#         'ambience_images': ambience_images,
#         'food_count': food_images.count(),
#         'ambience_count': ambience_images.count(),
#         'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,  # ✅ Add this
#         'menu_data': menu_data,
#         'reviews': reviews,
#         'avg_rating': round(rating_stats['avg_rating'] or 0, 1),
#         'total_reviews': rating_stats['total'],
#     }
#     return render(request, 'users/user_side/pepito.html', context)


# def cuisine_page(request, slug):
#     # Page content for heading, description, background
#     # page_content = get_object_or_404(CuisinePageContent, cuisine_name__iexact=cuisine)
#     page_content = get_object_or_404(CuisinePageContent, slug=slug)
    
#     cuisine = page_content.cuisine_name
    
#     # Approved restaurants with matching cuisine
#     restaurants = (
#         Restaurant.objects.filter(cuisine__icontains=cuisine, is_approved=True)
#         .prefetch_related('images')
#     )

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

#     return render(request, 'users/user_side/spots.html', {
#         'restaurant_data': restaurant_data,
#         'page_content': page_content,
#         'cuisine_name': cuisine,
#     })
    

# Updated views.py (assuming this is in your restaurants/views.py or similar)
# I've included the original two views and added the new search_suggestions view.
# Make sure to add all necessary imports at the top.

# Updated views.py (assuming this is in your restaurants/views.py or similar)
# I've included the original two views and added the new search_suggestions view.
# Make sure to add all necessary imports at the top.

# Updated views.py (assuming this is in your restaurants/views.py or similar)
# I've included the original two views and added the new search_suggestions view.
# Make sure to add all necessary imports at the top.

# Updated views.py (assuming this is in your restaurants/views.py or similar)
# I've included the original two views and added the new search_suggestions view.
# Make sure to add all necessary imports at the top.

from django.shortcuts import render, get_object_or_404
from itertools import islice
from django.utils import timezone
from django.db.models import Prefetch
from .models import Restaurant, MenuCategory, MenuItem, Review
from adminpanel.models import CuisinePageContent
from django.db.models import Q, Avg, Count
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.urls import reverse
# Add any other imports as needed, e.g., from restaurants.models import *

def cuisine_page(request, slug):
    # Page content for heading, description, background
    # page_content = get_object_or_404(CuisinePageContent, cuisine_name__iexact=cuisine)
    page_content = get_object_or_404(CuisinePageContent, slug=slug)
    
    cuisine = page_content.cuisine_name
    
    # Approved restaurants with matching cuisine
    restaurants = (
        Restaurant.objects.filter(cuisine__icontains=cuisine, is_approved=True)
        .prefetch_related('images', 'reviews')
    )
    restaurant_data = []
    for restaurant in restaurants:
        preview_image = (
            restaurant.images.first().image.url
            if restaurant.images.exists()
            else '/static/users/assets/img/about.jpg'
        )
        dining_reviews = restaurant.reviews.filter(visit_type__in=['Dine-In', 'Takeaway'])
        dining_stats = dining_reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
        restaurant_data.append({
            'restaurant': restaurant,
            'preview_image': preview_image,
            'dining_avg': round(dining_stats['avg_rating'] or 0, 1),
            'dining_count': dining_stats['total'],
        })
    return render(request, 'users/user_side/spots.html', {
        'restaurant_data': restaurant_data,
        'page_content': page_content,
        'cuisine_name': cuisine,
    })

@ensure_csrf_cookie
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
    dining_reviews = reviews.filter(visit_type__in=['Dine-In', 'Takeaway'])
    delivery_reviews = reviews.filter(visit_type='Delivery')
    dining_stats = dining_reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
    delivery_stats = delivery_reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
    context = {
        'restaurant': restaurant,
        'images': all_images,  # for full gallery
        'preview_images': preview_images,  # for the 4-image preview section
        'food_images': food_images,        # optional if you're categorizing in template
        'ambience_images': ambience_images,
        'food_count': food_images.count(),
        'ambience_count': ambience_images.count(),
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,  # ✅ Add this
        'menu_data': menu_data,
        'reviews': reviews,
        'dining_avg': round(dining_stats['avg_rating'] or 0, 1),
        'dining_count': dining_stats['total'],
        'delivery_avg': round(delivery_stats['avg_rating'] or 0, 1),
        'delivery_count': delivery_stats['total'],
    }
    return render(request, 'users/user_side/pepito.html', context)
    
def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    results = []
    if len(query) >= 2:
        # Search restaurants
        restaurants = Restaurant.objects.filter(name__icontains=query, is_approved=True)[:10]
        for r in restaurants:
            results.append({
                'type': 'restaurant',
                'name': r.name,
                'logo': r.logo.url if r.logo else '/static/default-logo.jpg',
                'location': r.address,
                'url': reverse('restaurants:restaurant_detail', kwargs={'slug': r.slug})
            })

        # Search cuisines
        cuisines = CuisinePageContent.objects.filter(cuisine_name__icontains=query)[:10]
        for c in cuisines:
            results.append({
                'type': 'cuisine',
                'name': c.cuisine_name,
                'image': c.background_image.url if c.background_image else '/static/default-cuisine.jpg',
                'url': reverse('restaurants:cuisine_page', kwargs={'slug': c.slug})  # Assuming URL name is 'restaurants:cuisine_page'
            })

        # Search dishes (menu items)
        menu_items = MenuItem.objects.filter(name__icontains=query, is_available=True)[:10]
        for m in menu_items:
            results.append({
                'type': 'dish',
                'name': m.name,
                'image': m.image.url if m.image else '/static/default-dish.jpg',
                'price': str(m.price),
                'restaurant': m.restaurant.name,
                'url': reverse('restaurants:restaurant_detail', kwargs={'slug': m.restaurant.slug})
            })

    return JsonResponse({'results': results})


from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from datetime import datetime
import json

@csrf_exempt
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





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import RestaurantForm, OwnerProfileForm  # Assuming forms are defined
from .models import RestaurantOwnerProfile, Restaurant

# Assume extract_from_text, CUISINES, CITIES are defined somewhere

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import RestaurantForm, OwnerProfileForm  # Assuming forms are defined
from .models import RestaurantOwnerProfile, Restaurant

# Assume extract_from_text, CUISINES, CITIES are defined somewhere

@login_required
def restaurant_create_view(request):
    """
    Owner onboarding - ek hi page par Restaurant + OwnerProfile (GST आदि) भरते हैं.
    """

    # Check if user has restaurant owner role
    if request.user.role != 'owner':  # Assuming User model has 'role' field with 'owner' value
        return redirect("authentication/loginsignup/")  # Redirect to login if not owner

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








# Razorpay payment logic

# import json
# import logging  # Added for better error logging
# import razorpay
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie  # Added ensure_csrf_cookie
# from django.shortcuts import get_object_or_404, render, redirect
# from .models import Order, TableBooking  # Adjust as needed

# logger = logging.getLogger(__name__)  # Added logger

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# @csrf_exempt
# def create_razorpay_order(request):
#     if request.method == 'POST':
#         try:
#             # Handle JSON body (for orders from cart)
#             if request.content_type == 'application/json':
#                 data = json.loads(request.body)
#                 amount = int(data.get('total_price', 0)) * 100  # Use 'total' from JS, convert to paise
#                 items = data.get('items', [])  # List of cart items
#                 restaurant_id = data.get('restaurant_id')
#                 booking_id = None  # Not a booking
#             # Handle form data (for bookings)
#             else:
#                 amount = int(request.POST.get("amount", 0)) * 100  # Convert to paise
#                 items = []  # No items for booking
#                 restaurant_id = None
#                 booking_id = request.POST.get('booking_id')

#             if amount <= 0:
#                 logger.warning("Invalid amount received: %s", amount)  # Log warning
#                 return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

#             currency = "INR"
#             notes = {"platform": "ZaykaZone"}

#             razorpay_order = client.order.create({
#                 "amount": amount,
#                 "currency": currency,
#                 "payment_capture": "1",  # Auto-capture
#                 "notes": notes
#             })

#             # Link to DB based on type
#             if booking_id:
#                 booking = get_object_or_404(TableBooking, id=booking_id)
#                 booking.razorpay_order_id = razorpay_order['id']
#                 booking.save()
#             else:
#                 # Create Order for cart (adjust to your Order model)
#                 order = Order.objects.create(
#                     user=request.user,
#                     restaurant_id=restaurant_id,
#                     total=amount / 100,  # Store in rupees
#                     razorpay_order_id=razorpay_order['id']
#                     # Add items as JSON or related models
#                 )
#                 # If items need saving as related models, loop here: for item in items: OrderItem.objects.create(order=order, ...)

#             logger.info("Razorpay order created: %s", razorpay_order['id'])  # Log success
#             return JsonResponse({
#                 "success": True,
#                 "id": razorpay_order['id'],
#                 "amount": amount  # In paise (Razorpay displays it automatically in modal)
#             })
#         except ValueError as e:
#             logger.error("Invalid data: %s", str(e))  # Log error
#             return JsonResponse({"error": f"Invalid data: {str(e)}"}, status=400)
#         except razorpay.errors.BadRequestError as e:
#             logger.error("Razorpay error: %s", str(e))
#             return JsonResponse({"error": f"Razorpay error: {str(e)}"}, status=400)
#         except Exception as e:
#             logger.error("Server error: %s", str(e))
#             return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
#     return JsonResponse({"error": "Invalid request method"}, status=405)


# @csrf_exempt
# @login_required  # Add this to ensure user is authenticated (matches your normal view)
# def create_razorpay_order(request):
#     if request.method == 'POST':
#         try:
#             # Handle JSON body (for orders from cart)
#             if request.content_type == 'application/json':
#                 data = json.loads(request.body)
#                 amount = int(data.get('total_price', 0)) * 100  # Convert to paise
#                 items = data.get('items', [])  # List of cart items
#                 restaurant_id = data.get('restaurant_id')
#                 booking_id = None  # Not a booking
#             # Handle form data (for bookings)
#             else:
#                 amount = int(request.POST.get("amount", 0)) * 100  # Convert to paise
#                 items = []  # No items for booking
#                 restaurant_id = None
#                 booking_id = request.POST.get('booking_id')

#             if amount <= 0:
#                 logger.warning("Invalid amount received: %s", amount)
#                 return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

#             currency = "INR"
#             notes = {"platform": "ZaykaZone"}

#             razorpay_order = client.order.create({
#                 "amount": amount,
#                 "currency": currency,
#                 "payment_capture": "1",  # Auto-capture
#                 "notes": notes
#             })

#             # Link to DB based on type
#             if booking_id:
#                 booking = get_object_or_404(TableBooking, id=booking_id)
#                 booking.razorpay_order_id = razorpay_order['id']
#                 booking.save()
#             else:
#                 # Fetch restaurant object (assuming ForeignKey named 'restaurant')
#                 restaurant = get_object_or_404(Restaurant, id=restaurant_id)
                
#                 # Create Order for cart
#                 order = Order.objects.create(
#                     user=request.user,  # Changed from 'user' to 'customer' to match model
#                     restaurant=restaurant,  # Use object if ForeignKey; if it's 'restaurant_id', change to restaurant_id=restaurant_id
#                     total_price=amount / 100,  # Changed from 'total' to 'total_price'
#                     razorpay_order_id=razorpay_order['id']
#                     # Add other fields like status='pending' if required by model
#                 )
                
#                 # Create related OrderItems
#                 for item in items:
#                     menu_item = get_object_or_404(MenuItem, id=item['id'])  # Fetch MenuItem
#                     OrderItem.objects.create(
#                         order=order,
#                         menu_item=menu_item,
#                         quantity=item['quantity'],
#                         price_at_order=item['price']  # Or menu_item.price if you want to use the stored price
#                     )

#             logger.info("Razorpay order created: %s", razorpay_order['id'])
#             return JsonResponse({
#                 "success": True,
#                 "id": razorpay_order['id'],
#                 "amount": amount  # In paise
#             })
#         except ValueError as e:
#             logger.error("Invalid data: %s", str(e))
#             return JsonResponse({"error": f"Invalid data: {str(e)}"}, status=400)
#         except razorpay.errors.BadRequestError as e:
#             logger.error("Razorpay error: %s", str(e))
#             return JsonResponse({"error": f"Razorpay error: {str(e)}"}, status=400)
#         except Exception as e:
#             logger.error("Server error: %s", str(e))
#             return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
#     return JsonResponse({"error": "Invalid request method"}, status=405)


# @csrf_exempt
# def payment_success(request):
#     if request.method == 'POST':
#         data = request.POST
        
#         logger.info(f"Payment success callback received: {dict(data)}")
        
#         try:
#             # Verify signature
#             client.utility.verify_payment_signature({
#                 'razorpay_order_id': data['razorpay_order_id'],
#                 'razorpay_payment_id': data['razorpay_payment_id'],
#                 'razorpay_signature': data['razorpay_signature']
#             })
            
#             logger.info(f"Signature verified for order: {data['razorpay_order_id']}")

#             payment_type = data.get('type', 'order')
            
#             if payment_type == 'booking':
#                 try:
#                     booking = TableBooking.objects.get(razorpay_order_id=data['razorpay_order_id'])
#                     booking.payment_status = "paid"
#                     booking.razorpay_payment_id = data['razorpay_payment_id']
#                     booking.save()
#                     redirect_url = '/booking-confirmation/'
#                     logger.info(f"Booking {booking.id} payment successful")
#                 except TableBooking.DoesNotExist:
#                     logger.error(f"Booking not found for order_id: {data['razorpay_order_id']}")
#                     return JsonResponse({"status": "Booking not found"}, status=404)
#             else:
#                 try:
#                     order = Order.objects.get(razorpay_order_id=data['razorpay_order_id'])
#                     order.payment_status = "paid"
#                     order.razorpay_payment_id = data['razorpay_payment_id']
#                     order.razorpay_signature = data['razorpay_signature']
#                     order.status = 'confirmed'  # Update order status
#                     order.save()
#                     redirect_url = f'/order-confirmation/{order.id}/'
#                     logger.info(f"Order {order.id} payment successful")
#                 except Order.DoesNotExist:
#                     logger.error(f"Order not found for razorpay_order_id: {data['razorpay_order_id']}")
#                     # Check if order exists at all
#                     all_orders = Order.objects.filter(user=request.user).values_list('id', 'razorpay_order_id')
#                     logger.error(f"Available orders for user: {list(all_orders)}")
#                     return JsonResponse({"status": "Order not found"}, status=404)

#             return JsonResponse({"status": "Payment successful", "redirect_url": redirect_url})
            
#         except razorpay.errors.SignatureVerificationError as e:
#             logger.error(f"Signature verification failed: {str(e)}")
#             return JsonResponse({"status": "Payment verification failed"}, status=400)
#         except KeyError as e:
#             logger.error(f"Missing required field: {str(e)}")
#             return JsonResponse({"status": f"Missing field: {str(e)}"}, status=400)
#         except Exception as e:
#             logger.error(f"Unexpected error in payment_success: {str(e)}", exc_info=True)
#             return JsonResponse({"status": f"Error: {str(e)}"}, status=500)
    
#     return JsonResponse({"error": "Invalid request method"}, status=405)





from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import razorpay
import json
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client (do this once, at module level)
client = razorpay.Client(auth=("rzp_test_ROa0H24lCuEtfC", "rKBun7IfqORb96Lbdud7jHVZ"))

@csrf_exempt
@login_required
def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            # Handle JSON body (for orders from cart)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                amount = int(float(data.get('total_price', 0)) * 100)  # Convert to paise
                items = data.get('items', [])
                restaurant_id = data.get('restaurant_id')
                order_type = 'order'
            # Handle form data (for bookings)
            else:
                amount = int(float(request.POST.get("amount", 0)) * 100)
                items = []
                restaurant_id = None
                booking_id = request.POST.get('booking_id')
                order_type = 'booking'

            if amount <= 0:
                return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

            # Create Razorpay order
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })

            # Save order details to database
            if order_type == 'booking':
                booking = get_object_or_404(TableBooking, id=booking_id)
                booking.total_amount=amount / 100  # Store in rupees
                booking.razorpay_order_id = razorpay_order['id']
                booking.save()
            else:
                restaurant = get_object_or_404(Restaurant, id=restaurant_id)
                order = Order.objects.create(
                    user=request.user,
                    restaurant=restaurant,
                    total_price=amount / 100,
                    razorpay_order_id=razorpay_order['id'],
                    status='pending'
                )
                
                # Create OrderItems
                for item in items:
                    menu_item = get_object_or_404(MenuItem, id=item['id'])
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=item['quantity'],
                        price_at_order=item['price']
                    )

            logger.info(f"Razorpay order created: {razorpay_order['id']}")
            return JsonResponse({
                "success": True,
                "id": razorpay_order['id'],
                "amount": amount,
                "currency": "INR"
            })

        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        response=request.POST
        # print(response)
        params_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']        
        }
        #client instance
        client=razorpay.Client(auth=("rzp_test_ROa0H24lCuEtfC","rKBun7IfqORb96Lbdud7jHVZ"))
        
        try:
            status=client.utility.verify_payment_signature(params_dict)
            payment_type = request.POST.get('type', 'order')
            
            if payment_type == 'booking':
                booking = TableBooking.objects.get(razorpay_order_id=response['razorpay_order_id'])
                booking.razorpay_payment_id = response['razorpay_payment_id']
                booking.razorpay_signature = response['razorpay_signature']
                booking.paid=True
                booking.save()
                # return render(request,'payment_status.html',{'status':True})
                return JsonResponse({
    "status": "Payment successful",
    "razorpay_order_id": response['razorpay_order_id'],
    "razorpay_payment_id": response['razorpay_payment_id'],
    "razorpay_signature": response['razorpay_signature'],
    "redirect_url": reverse("restaurants:table_booking_confirmation", args=[booking.id])
})
            else:
                order = Order.objects.get(razorpay_order_id=response['razorpay_order_id'])
                order.razorpay_payment_id = response['razorpay_payment_id']
                order.razorpay_signature = response['razorpay_signature']
                order.paid=True
                order.save()
                # return render(request,'users/user_side/order_confirmation.html',{'status':True})
                return JsonResponse({
    "status": "Payment successful",
    "razorpay_order_id": response['razorpay_order_id'],
    "razorpay_payment_id": response['razorpay_payment_id'],
    "razorpay_signature": response['razorpay_signature'],
    "redirect_url": reverse("restaurants:order_confirmation", args=[order.id])
})

        except:
            return render(request,'users/user_side/pepito.html',{'status':False})
    
    return JsonResponse({"error": "Invalid request method"}, status=405)



from django.shortcuts import render
from django.conf import settings

def payment_page(request):
    response=request.POST
    # Assume amount and other data from session or DB
    amount = 500  # Dynamic from your logic
    amount_in_paise = amount * 100
    # Call create_razorpay_order internally or via AJAX
    # For simplicity, assume you create order here or pass from previous step
    razorpay_order_id = 'your_generated_order_id'  # From create_razorpay_order

    context = {
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'amount_in_paise': amount_in_paise,
        'razorpay_order_id': razorpay_order_id,
        'user': request.user  # Assuming auth
    }
    return render(request, 'users/user_side/pepito.html', context)





# from django.shortcuts import render, redirect
# from restaurants.views import create_razorpay_order  # Import if in different app
# from django.http import HttpResponseBadRequest

# def pepito_view(request):
#     # Your logic for displaying restaurants
#     restaurants = [...]  # Fetch data

#     if request.method == 'POST':
#         # Handle booking form submission
#         amount = request.POST.get('amount')
#         booking_id = [...]  # Create booking and get ID
#         # Simulate create_razorpay_order call
#         order_response = create_razorpay_order(request)  # Pass request
#         if order_response.status_code != 200:
#             return HttpResponseBadRequest("Order creation failed")
#         razorpay_order = order_response.json()
#         context = {
#             'restaurants': restaurants,
#             'show_payment_form': True,
#             'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
#             'amount_in_paise': int(amount) * 100,
#             'razorpay_order_id': razorpay_order['id'],
#             'user': request.user
#         }
#         return render(request, 'users/pepito.html', context)

#     return render(request, 'users/pepito.html', {'restaurants': restaurants})

# ... (add your other views here)





#Razorpay payment logic

# import json
# import razorpay
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.shortcuts import get_object_or_404
# from .models import Order, TableBooking  # Adjust as needed

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# @csrf_exempt
# def create_razorpay_order(request):
#     if request.method == 'POST':
#         try:
#             # Handle JSON body (for orders from cart)
#             if request.content_type == 'application/json':
#                 data = json.loads(request.body)
#                 amount = int(data.get('total', 0)) * 100  # Use 'total' from JS, convert to paise
#                 items = data.get('items', [])  # List of cart items
#                 restaurant_id = data.get('restaurant_id')
#                 booking_id = None  # Not a booking
#             # Handle form data (for bookings)
#             else:
#                 amount = int(request.POST.get("amount", 0)) * 100  # Convert to paise
#                 items = []  # No items for booking
#                 restaurant_id = None
#                 booking_id = request.POST.get('booking_id')

#             if amount <= 0:
#                 return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

#             currency = "INR"
#             notes = {"platform": "ZaykaZone"}

#             razorpay_order = client.order.create({
#                 "amount": amount,
#                 "currency": currency,
#                 "payment_capture": "1",  # Auto-capture
#                 "notes": notes
#             })

#             # Link to DB based on type
#             if booking_id:
#                 booking = get_object_or_404(TableBooking, id=booking_id)
#                 booking.razorpay_order_id = razorpay_order['id']
#                 booking.save()
#             else:
#                 # Create Order for cart (adjust to your Order model)
#                 order = Order.objects.create(
#                     user=request.user,
#                     restaurant_id=restaurant_id,
#                     total=amount / 100,  # Store in rupees
#                     razorpay_order_id=razorpay_order['id']
#                     # Add items as JSON or related models
#                 )
#                 # If items need saving as related models, loop here: for item in items: OrderItem.objects.create(order=order, ...)

#             return JsonResponse({
#                 "success": True,
#                 "id": razorpay_order['id'],
#                 "amount": amount  # In paise (Razorpay displays it automatically in modal)
#             })
#         except ValueError as e:
#             return JsonResponse({"error": f"Invalid data: {str(e)}"}, status=400)
#         except razorpay.errors.BadRequestError as e:
#             return JsonResponse({"error": f"Razorpay error: {str(e)}"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
#     return JsonResponse({"error": "Invalid request method"}, status=405)

# @csrf_exempt  # Exempt CSRF for Razorpay callback
# def payment_success(request):
#     if request.method == 'POST':
#         data = request.POST
#         try:
#             # Verify signature
#             client.utility.verify_payment_signature({
#                 'razorpay_order_id': data['razorpay_order_id'],
#                 'razorpay_payment_id': data['razorpay_payment_id'],
#                 'razorpay_signature': data['razorpay_signature']
#             })

#             # Update DB: Find by razorpay_order_id
#             booking = TableBooking.objects.get(razorpay_order_id=data['razorpay_order_id'])  # Or Order
#             booking.payment_status = "paid"
#             booking.payment_id = data['razorpay_payment_id']
#             booking.save()

#             return JsonResponse({"status": "Payment successful"})
#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({"status": "Payment verification failed"}, status=400)
#         except TableBooking.DoesNotExist:
#             return JsonResponse({"status": "Booking not found"}, status=400)
#     return JsonResponse({"error": "Invalid request method"}, status=405)




# from django.shortcuts import render
# from django.conf import settings

# def payment_page(request):
#     # Assume amount and other data from session or DB
#     amount = 500  # Dynamic from your logic
#     amount_in_paise = amount * 100
#     # Call create_razorpay_order internally or via AJAX
#     # For simplicity, assume you create order here or pass from previous step
#     razorpay_order_id = 'your_generated_order_id'  # From create_razorpay_order

#     context = {
#         'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
#         'amount_in_paise': amount_in_paise,
#         'razorpay_order_id': razorpay_order_id,
#         'user': request.user  # Assuming auth
#     }
#     return render(request, 'users/pepito.html', context)





# from django.shortcuts import render, redirect
# from restaurants.views import create_razorpay_order  # Import if in different app
# from django.http import HttpResponseBadRequest

# def pepito_view(request):
#     # Your logic for displaying restaurants
#     restaurants = [...]  # Fetch data

#     if request.method == 'POST':
#         # Handle booking form submission
#         amount = request.POST.get('amount')
#         booking_id = [...]  # Create booking and get ID
#         # Simulate create_razorpay_order call
#         order_response = create_razorpay_order(request)  # Pass request
#         if order_response.status_code != 200:
#             return HttpResponseBadRequest("Order creation failed")
#         razorpay_order = order_response.json()
#         context = {
#             'restaurants': restaurants,
#             'show_payment_form': True,
#             'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
#             'amount_in_paise': int(amount) * 100,
#             'razorpay_order_id': razorpay_order['id'],
#             'user': request.user
#         }
#         return render(request, 'users/pepito.html', context)

#     return render(request, 'users/pepito.html', {'restaurants': restaurants})

