from django.contrib import admin
from .models import CuisinePageContent
from users.models import User  # Import your custom user model

# Register your models here.
class CuisinePageContentAdmin(admin.ModelAdmin):
    # ✅ Show these fields in the admin list view
    list_display = ('cuisine_name', 'title', 'description', 'background_image')

    # ✅ Allow search by these fields
    search_fields = ('cuisine_name', 'title')

    # ✅ Optional: fields to show as readonly (e.g. created_at, etc.)
    # readonly_fields = ('created_at',)
    def is_admin_role(self, request):
        user = request.user
        # ✅ Allow access if user is superuser OR role is 'admin'
        return user.is_superuser or (isinstance(user, User) and user.role == 'admin')

    def has_module_permission(self, request):
        return self.is_admin_role(request)

    def has_view_permission(self, request, obj=None):
        return self.is_admin_role(request)

    def has_change_permission(self, request, obj=None):
        return self.is_admin_role(request)

    def has_add_permission(self, request):
        return self.is_admin_role(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_admin_role(request)



admin.site.register(CuisinePageContent, CuisinePageContentAdmin)
