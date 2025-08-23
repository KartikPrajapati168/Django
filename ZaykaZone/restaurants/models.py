from django.db import models
from users.models import User
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Restaurant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants',null=False, blank=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)  # ✅ Add this line
    logo = models.ImageField(upload_to='restaurants/restaurant_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    dining_out_available = models.BooleanField(default=False)
    timings = models.CharField(max_length=100)
    
     # Optional visual name of the owner
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    
    city = models.CharField(max_length=100, blank=True, null=True)
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Default: Not approved
    
    
    
    @property
    def display_owner_name(self):
        """Alias to get updated owner name."""
        return (
            getattr(self.owner.owner_profile, "full_name", None)
            or self.owner.full_name
        )
        
    def __str__(self):
        #यह Python का special (dunder) method है। Admin या Django shell में जब किसी Restaurant ऑब्जेक्ट को print करते हैं, तो यह method कॉल होता है।
        return self.name
    
    
     
    def save(self, *args, **kwargs):
        # ── ① create slug automatically ────────────────────────────────
     if not self.slug:                             # slug empty?
        base_slug = slugify(self.name)            # e.g. "Pepito"
        slug = base_slug
        counter = 1
        # guarantee uniqueness if another restaurant already has that slug
        #डेटाबेस में चेक: क्या यही slug पहले से किसी दूसरे रेस्टोरेंट की row में है? (exclude(pk=self.pk) का मतलब—अपनी ही row को इग्नोर करो, ताकि edit पर clash न हो)।
        while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"       # pepito‑1, pepito‑2, …
            #	पायथन f‑string से "pepito-bistro-1", "pepito-bistro-2" बनाते जाते हैं।
            counter += 1
        self.slug = slug

    # ── ② (your existing cuisine / city extraction below) ───────────
        # List of cuisines and cities
        # CUISINES = [
        #     'spots', 'legendary', 'buffets', 'gujarati thali',
        #     'asian restaurant', 'rollins with dosas'
        # ]
        # CITIES = ['ahmedabad']

        # def extract_from_text(text, options):
        #     if not text:
        #         return None
        #     text = text.lower()
        #     for item in options:
        #         if item.lower() in text:
        #             return item.title()
        #     return None

        # self.cuisine = extract_from_text(self.description, CUISINES)
        # self.city = extract_from_text(self.address, CITIES)
        
     # Automatically set owner_name from owner_profile if available
     if not self.owner_name and hasattr(self.owner, 'restaurantownerprofile'):
            self.owner_name = self.owner.restaurantownerprofile.full_name
            
     super().save(*args, **kwargs)
     
     


# class RestaurantOwnerProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_profile')
#     gst_number = models.CharField(max_length=20, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.full_name}'s Profile"


class RestaurantApprovalRequest(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)  # ✅ Add this

    def __str__(self):
        return f"Approval request: {self.restaurant.name}"
    
    @property
    def is_pending(self):
       return not self.is_approved and not self.is_rejected


class RestaurantOwnerProfile(models.Model):
    """
    ONE profile per restaurant-owner user.
    Stores personal / compliance info that is **not** specific
    to a single restaurant menu.
    """
    user        = models.OneToOneField(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    related_name='owner_profile')

    full_name   = models.CharField(max_length=100, blank=True)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=20, blank=True)

    gst_number  = models.CharField(max_length=20, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    @receiver(post_save, sender=User)
    def update_owner_profile_name(sender, instance, **kwargs):
        if hasattr(instance, 'restaurantownerprofile'):
           profile = instance.restaurantownerprofile
           new_name = instance.get_full_name()
           if new_name and profile.full_name != new_name:
              profile.full_name = new_name
              profile.save()
    
    def __str__(self):
        return self.full_name or self.user.full_name or self.user.email


class RestaurantImage(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('ambience', 'Ambience'),
    ]

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='restaurants/photos/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ✅ New field to mark preview images (right side 4 photos)
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.restaurant.name} - {self.category} {'(Preview)' if self.is_preview else ''}"
    
    
    


class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name='menu_categories', null=True, blank=True
    )
    image = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    is_global = models.BooleanField(default=False)  # True = fixed system category

    def __str__(self):
        if self.is_global:
            return f"{self.name} (Global)"
        return f"{self.name} ({self.restaurant.name})"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',null=True, blank=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})" if self.restaurant else self.name
    
    

class TableBooking(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    date = models.DateField()
    time = models.TimeField()
    no_of_guests = models.PositiveIntegerField()
    meal_type = models.CharField(
        max_length=10,
        choices=[('lunch', 'Lunch'), ('dinner', 'Dinner')]
    )
    message = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or self.user} - {self.restaurant.name} on {self.date}"

# class Review(models.Model):
#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     comment = models.TextField()
#     rating = models.PositiveIntegerField()  # 1 to 5
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Review by {self.user.email} for {self.restaurant.name}" if self.user else "Review"

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Review details
    visit_date = models.DateField(null=True, blank=True)
    visit_type = models.CharField(max_length=20, choices=[
        ('Dine-In', 'Dine-In'),
        ('Takeaway', 'Takeaway'),
        ('Delivery', 'Delivery')
    ],null=True, blank=True)
    
    # Ratings (1-5 scale)
    rating = models.PositiveIntegerField(null=True, blank=True)  # Overall rating
    food_quality = models.PositiveIntegerField(null=True, blank=True)
    service_quality = models.PositiveIntegerField(null=True, blank=True)
    
    # Comment
    comment = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        # Prevent duplicate reviews from same user for same restaurant
        unique_together = ['restaurant', 'user', 'visit_date']

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Anonymous"
        return f"Review by {user_name} for {self.restaurant.name}"

    @property
    def user_display_name(self):
        """Return user's full name or username"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return "Anonymous"

    def clean(self):
        """Validate rating values"""
        from django.core.exceptions import ValidationError
        
        ratings = [self.rating, self.food_quality, self.service_quality]
        for rating in ratings:
            if rating and (rating < 1 or rating > 5):
                raise ValidationError("Ratings must be between 1 and 5")
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.email}"
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item')  # Prevents duplicates

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity} (Cart)"
