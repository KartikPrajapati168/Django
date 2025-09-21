from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from restaurants.models import Restaurant
from restaurants.forms import TableBookingForm
from django.contrib.auth import  authenticate, login
from .models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


# Create your views here.
def login_signup(request):
    return render(request, 'users/authentication/loginsignup.html')


def index(request):
    restaurant = Restaurant.objects.first()  # This must not be None
    if not restaurant:
        return render(request, 'error.html', {'message': 'No restaurant found'})
    
    form = TableBookingForm()
    return render(
        request,
        'users/user_side/index.html',
        {'restaurant': restaurant, 'form': form}
    )

def index_asian(request):
    return render(request, 'users/user_side/asian.html')

def index_buffets(request):
    return render(request, 'users/user_side/buffets.html')

def index_gujarati(request):
    return render(request, 'users/user_side/gujarati.html')

def index_legendary(request):
    return render(request, 'users/user_side/legendary.html')

def index_pepito(request):
    # It seems from your urls.py that 'index_pepito' is tied to a fixed slug 'pepito'.
    # If the URL is `path('index/spots/pepito/', views.index_pepito, name='index_pepito')`,
    # then the view itself doesn't receive the slug as a parameter.
    # You would explicitly query for the restaurant with that slug.

    try:
        restaurant = get_object_or_404(Restaurant, slug='pepito')
    except Exception as e:
        # This block will catch if the restaurant with slug 'pepito' is not found
        # or if there's any other issue in retrieving it.
        print(f"Error retrieving restaurant 'pepito': {e}")
        # You might want to handle this gracefully, e.g., redirect or show an error page
        # For now, let's ensure 'restaurant' is set to None if not found
        restaurant = None # Set to None so we can check it later

    # --- Crucial Debugging Prints ---
    print("\n--- Debugging `index_pepito` View ---")
    print(f"Is 'restaurant' object None? {restaurant is None}")
    if restaurant:
        print(f"Restaurant name: {restaurant.name}")
        print(f"Restaurant ID: {restaurant.id}")
        print(f"Restaurant Slug: {restaurant.slug}")
    else:
        print("Restaurant object could not be retrieved. Check your database for a 'pepito' slug.")
    print("------------------------------------\n")
    # --- End Debugging Prints ---

    context = {
        'restaurant': restaurant,
        # Ensure you're passing other required context like
        # 'preview_images', 'all_images', 'food_images', 'ambience_images',
        # 'menu_categories' if they are used elsewhere in your template.
        # If any of these are missing, they might cause other errors.
    }
    return render(request, 'users/user_side/pepito.html', context) # Make 

def index_rollins(request):
    return render(request, 'users/user_side/Rollins.html')

def index_spots(request):
    return render(request, 'users/user_side/spots.html')

def index_spots(request):
    return render(request, 'users/user_side/spots.html')

def index_starterpage(request):
    return render(request, 'users/user_side/starter-page.html')



def register_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        country_code = request.POST.get('country_code') or '+91'
        full_phone = f"{country_code}{phone}"

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('/login')  # Redirect back to the signup page

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=name,
            role=role,
            country_code=country_code,
            phone=phone,
            full_phone=full_phone
        )

        # Set backend explicitly to avoid ValueError
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        # Redirect based on role
        if role == "restaurant":
            return redirect('/restaurant/profile/settings/')
        elif role == "admin":
            return redirect('admin-dashboard/')
        else:
            return redirect('index/')

    return redirect('/login')





# def register_user(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         role = request.POST.get('role')
#         phone = request.POST.get('phone')
#         country_code = request.POST.get('country_code') or '+91'  # You can pass this using JS
#         full_phone = f"{country_code}{phone}"

#         if User.objects.filter(email=email).exists():
#             return render(request, 'users/loginsignup.html', {'error': 'Email already exists.'})

#         user = User.objects.create_user(
#             email=email,
#             password=password,
#             full_name=name,
#             role=role,
#             country_code=country_code,
#             phone=phone,
#             full_phone=full_phone
#         )
#         login(request, user)  # Auto login after signup

#         if role == "restaurant":
#             return redirect('/restaurant/profile/settings/')
#         elif role == "admin":
#             return redirect('/adminpanel/dashboard/')
#         else:
#             return redirect('/')

#     return redirect('/')

from restaurants.models import RestaurantOwnerProfile

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.role != role:
                return render(request, 'users/authentication/loginsignup.html', {'error': 'Incorrect role selected.'})
            
            login(request, user)
            

            if role == "restaurant":
                # # Ensure owner profile exists
                # RestaurantOwnerProfile.objects.get_or_create(user=user)
                
                # # Get approved restaurants for current user
                # approved_restaurants = Restaurant.objects.filter(
                #     owner=user, 
                #     is_approved=True
                # )
                 # ✅ ensure profile exists (no duplicate creation)
                owner_profile, created = RestaurantOwnerProfile.objects.get_or_create(user=user)
                
                # Agar galti se multiple profiles hain, toh ek ko rakhkar baaki delete kar do
                extra_profiles = RestaurantOwnerProfile.objects.filter(user=user).exclude(id=owner_profile.id)
                if extra_profiles.exists():
                    extra_profiles.delete()

                # ✅ get all restaurants linked to this owner profile
                approved_restaurants = Restaurant.objects.filter(
                    # owner_profile__user=user, 
                    owner_profile=owner_profile, # 🔑 relation via owner_profile
                    is_approved=True
                )
                
                if not approved_restaurants.exists():
                    return redirect('restaurants:restaurant_approval_pending')
                
                elif approved_restaurants.count() == 1:
                    # Redirect to dashboard with restaurant ID
                    restaurant = approved_restaurants.first()
                    return redirect('restaurants:dashboard', slug=restaurant.slug)
                
                else:
                    # Redirect to restaurant selection page
                    return redirect('users:select_restaurant')
                    
            elif role == "admin":
                return redirect('adminpanel:admin_dashboard')
            else:
                return redirect('/index/')
        else:
            return render(request, 'users/authentication/loginsignup.html', {'error': 'Invalid credentials'})

    return redirect('/')





@login_required
def after_login_redirect(request):
    user = request.user
    restaurants = Restaurant.objects.filter(owner=user)

    if restaurants.count() == 1:
        # agar sirf ek restaurant he, uska slug leke dashboard pe redirect kar do
        return redirect('restaurants:dashboard', slug=restaurants.first().slug)
    elif restaurants.count() > 1:
        # agar multiple restaurants hain to selection page pe bhejo
        return redirect('users:select_restaurant')
    else:
        # koi restaurant hi nahi mila
        messages.warning(request, "No restaurant found for your account.")
        return redirect('create_restaurant')  # ya koi fallback page

# @login_required
# def select_restaurant_view(request):
#     restaurants = Restaurant.objects.filter(owner=request.user)
#     return render(request, 'users/authentication/restaurant_selection.html', {'restaurants': restaurants})

from django.shortcuts import render, redirect
from restaurants.models import Restaurant


# def select_restaurant_view(request):
#     # ✅ Only allow restaurant owners to access this page
#     if not hasattr(request.user, 'restaurantownerprofile'):
#         # ⛔ Don't redirect back to this page — that causes a redirect loop
#         return render(request, 'users/authentication/access_denied.html', {
#             'message': 'You must be a restaurant owner to select a restaurant.'
#         })

#     # ✅ Get restaurants for this owner using owner_name
#     restaurants = Restaurant.objects.filter(
#         owner_name=request.user.restaurantownerprofile.full_name
#     )
    
#     context = {'restaurants': restaurants}
#     return render(request, 'users/authentication/restaurant_selection.html', context)

# def select_restaurant_view(request):
#     # Check if user has restaurant owner profile
#     if not request.user.is_authenticated:
#         return redirect('login')
    
#     # Get the owner's full name from the profile
#     if hasattr(request.user, 'restaurantownerprofile'):
#         owner_full_name = request.user.restaurantownerprofile.full_name
#     else:
#         # Fallback to first_name + last_name if profile exists
#         owner_full_name = f"{request.user.full_name}".strip()
#         if not owner_full_name:
#             # If no name is available, redirect to home
#             return redirect('home')
    
#     # Get restaurants for this owner (case-insensitive match)
#     restaurants = Restaurant.objects.filter(
#         owner_name__iexact=owner_full_name
#     )
    
#     # If no restaurants found, redirect to home
#     if not restaurants.exists():
#         return redirect('home')
    
#     # If only one restaurant exists, redirect to its dashboard
#     if restaurants.count() == 1:
#         return redirect('restaurants:dashboard', slug=restaurants.first().slug)
    
#     context = {'restaurants': restaurants}
#     return render(request, 'users/authentication/restaurant_selection.html', context)


@login_required
def select_restaurant_view(request):
    # Get the user's full name
    if not request.user.full_name:
        return redirect('home')
    
    # Get restaurants for this owner (case-insensitive)
    restaurants = Restaurant.objects.filter(
        owner_name__iexact=request.user.full_name,
        is_approved=True
    )
    
    # If no restaurants found, redirect to home
    if not restaurants.exists():
        return redirect('home')
    
    # If only one restaurant exists, redirect to its dashboard
    if restaurants.count() == 1:
        return redirect('restaurants:dashboard', slug=restaurants.first().slug)
    
    context = {'restaurants': restaurants}
    return render(request, 'users/authentication/restaurant_selection.html', context)

# def select_restaurant_view(request):
#     # Check if user is restaurant owner
#     if not hasattr(request.user, 'restaurantownerprofile'):
#         # Handle non-owner users appropriately
#         return redirect('users:select_restaurant')
    
#     # Get all restaurants for this owner using the owner_name field
#     restaurants = Restaurant.objects.filter(
#         owner_name=request.user.restaurantownerprofile.full_name
#     )
    
#     context = {'restaurants': restaurants}
#     return render(request, 'users/authentication/restaurant_selection.html', context)

# @login_required
# def select_restaurant_view(request):
#     # Get the RestaurantOwner profile for the logged-in user
#     owner_profile = request.user.restaurantowner
    
#     # Filter restaurants by the owner
#     restaurants = Restaurant.objects.filter(owner=owner_profile)
    
#     context = {'restaurants': restaurants}
#     return render(request, 'users/authentication/restaurant_selection.html', context)

def logout_view(request):
    logout(request)
    return redirect('login_signup')

def switch_account(request):
    if request.user.is_authenticated and request.user.role == 'customer':
        logout(request)
        return redirect('login_signup')
    return redirect('index')



# from restaurants.models import Restaurant  # ← yeh import zaruri hai

# def cuisine_view(request, cuisine_slug):
#     restaurants = Restaurant.objects.filter(
#         cuisine__iexact=cuisine_slug,  # case-insensitive match
#         is_approved=True
#     )
#     return render(request, 'users/user_side/spots.html', {
#         'restaurants': restaurants,
#         'cuisine': cuisine_slug
#     })
    
    
@csrf_exempt
def book_table(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        people = request.POST.get('people')
        message = request.POST.get('message')

        # Here, you can also save to the database if you want

        # Send email (optional)
        try:
            from django.core.mail import send_mail
            send_mail(
                subject="New table booking request",
                message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nDate: {date}\nTime: {time}\nPeople: {people}\nMessage: {message}",
                from_email=email,
                recipient_list=['your@email.com'],  # change this
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=f"From: {name}\nEmail: {email}\nMessage:\n{message}",
                from_email=email,
                recipient_list=['your@email.com'],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
