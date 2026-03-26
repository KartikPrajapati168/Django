from rest_framework.permissions import BasePermission

class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.role == "client":
            return user.clientprofile.status == "approved"

        elif user.role == "lawfirm":
            return user.lawfirmprofile.status == "approved"

        return True
    
    