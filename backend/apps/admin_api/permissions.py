from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsSuperUser(BasePermission):
    """Guards the levers that can create or destroy admin access."""

    message = 'فقط مدیر ارشد اجازه‌ی این کار را دارد.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
