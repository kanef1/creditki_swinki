from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Роли и профиль', {'fields': ('role', 'phone', 'position')}),
    )
    list_display = ['username', 'email', 'role', 'phone', 'position', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
