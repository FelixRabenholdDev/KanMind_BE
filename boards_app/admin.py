from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("fullname",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {
            "classes": ("wide",),
            "fields": ("email", "username", "fullname", "password1", "password2"),
        }),
    )

    list_display = ("email", "username", "fullname", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")

    search_fields = ("email", "username", "fullname")
    ordering = ("email",)

    readonly_fields = ()