from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class SupplierHubUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Supplier Hub", {"fields": ("preferred_language",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Supplier Hub", {"fields": ("email", "preferred_language")}),
    )

# Register your models here.
