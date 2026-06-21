from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, User


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['phone', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    inlines = [AddressInline]
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('phone', 'password1', 'password2')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'province', 'is_default']
    list_filter = ['province', 'is_default']
    search_fields = ['user__phone', 'city', 'receiver_name']
