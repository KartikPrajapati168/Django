# from django.contrib import admin
# from .models import Restaurant, RestaurantOwnerProfile,MenuCategory, MenuItem

# admin.site.register(Restaurant)
# admin.site.register(RestaurantOwnerProfile)
# admin.site.register(MenuCategory)
# admin.site.register(MenuItem)


from django.contrib import admin
from .models import Restaurant, RestaurantOwnerProfile, MenuCategory, MenuItem
from .models import RestaurantImage
from .utils import extract_from_text, CUISINES, CITIES
from django.utils.html import format_html
from users.models import User  # agar custom user use kar rahe ho
from .models import Review
from .models import RestaurantApprovalRequest
from .models import TableBooking
from .models import CartItem, Order, OrderItem





@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'is_global','image')
    list_filter = ('is_global',)
    search_fields = ('name', 'restaurant__name')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'restaurant', 'price', 'is_available')
    list_filter = ('category', 'restaurant', 'is_available')
    search_fields = ('name', 'description', 'restaurant__name')

# class RestaurantImageInline(admin.TabularInline):
#     model = RestaurantImage
#     extra = 1
    
    
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'set_owner_name','owner', 'city', 'cuisine', 'dining_out_available', 'is_approved')
    # inlines = [RestaurantImageInline]  # 💥 This line ensures safe FK linkage
    # # ... keep rest of your code unchanged
    list_filter = ('is_approved', 'city', 'cuisine')
    search_fields = ('name', 'owner__email')
    prepopulated_fields = {"slug": ("name",)}
    actions = ['approve_restaurants']
    
    # def get_owner_name(self, obj):
    #     return obj.owner_name if obj.owner_name else "Not Set"
    # get_owner_name.short_description = 'Set Owner Name'
    def set_owner_name(self, obj):
        # profile = RestaurantOwnerProfile.objects.filter(user=obj.owner).first()
        profile = RestaurantOwnerProfile.objects.filter(restaurant=obj).first()
        return profile.full_name if profile else "-"
    set_owner_name.short_description = "SET OWNER NAME"
    
    
    @admin.display(description="Owner")
    def owner_name(self, obj):
        # पहले प्रोफ़ाइल वाला नाम, वरना user.full_name
        profile = getattr(obj.owner, 'owner_profile', None)
        return profile.full_name if profile and profile.full_name else obj.owner.full_name
    
    def save_model(self, request, obj, form, change):
        # auto-fill karna agar blank ho
       if not obj.cuisine:
         obj.cuisine = extract_from_text(obj.description, CUISINES)
       if not obj.city:
         obj.city = extract_from_text(obj.address, CITIES)
       super().save_model(request, obj, form, change)

    def approve_restaurants(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} restaurant(s) approved successfully.")
    approve_restaurants.short_description = "Approve selected restaurants ✅"
    
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(role='Restaurant')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(RestaurantOwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'restaurant','email', 'phone', 'gst_number')
    search_fields = ('full_name', 'restaurant','email', 'phone', 'gst_number')
    

@admin.register(RestaurantImage)
class RestaurantImageAdmin(admin.ModelAdmin):
    list_display = ['display_image','restaurant','category', 'uploaded_at', 'is_preview']
    
    def display_image(self,obj):
        if obj.image:
            return format_html(f"<img src='{obj.image.url}' height='100'width='100'/>")
        return "Image not available"
    
    

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'visit_date','visit_type','rating','food_quality','service_quality','comment','created_at')
    list_filter = ('restaurant', 'rating', 'created_at')
    search_fields = ('restaurant__name', 'user__username', 'comment')
    
    
@admin.register(RestaurantApprovalRequest)
class RestaurantApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'created_at', 'is_approved', 'is_rejected')
    list_filter = ('is_approved', 'is_rejected')
    
    #if want to show only pending requests
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return [r for r in qs if r.is_pending]
    

@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date', 'time', 'no_of_guests', 'meal_type', 'restaurant')
    search_fields = ('name', 'email', 'phone', 'restaurant__name')
    list_filter = ('date', 'meal_type', 'restaurant')


# CartItem Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'quantity', 'added_at')
    list_filter = ('user', 'menu_item')
    search_fields = ('user__email', 'menu_item__name')

# OrderItem Inline (to show items inside Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # don't show extra blank row
    readonly_fields = ('menu_item', 'quantity', 'price_at_order')

# Order Admin with inline OrderItems
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'total_price', 'status', 'timestamp')
    list_filter = ('status', 'restaurant')
    search_fields = ('user__email', 'restaurant__name')
    inlines = [OrderItemInline]

# Optional: Register OrderItem separately if needed
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price_at_order')
    search_fields = ('order__user__email', 'menu_item__name')
    
