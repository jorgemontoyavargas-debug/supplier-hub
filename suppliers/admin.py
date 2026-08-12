from django.contrib import admin

from .models import (
    Category,
    ExternalSupplierCode,
    Supplier,
    SupplierCategory,
    SupplierContact,
)


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 0


class SupplierCategoryInline(admin.TabularInline):
    model = SupplierCategory
    extra = 0


class ExternalSupplierCodeInline(admin.TabularInline):
    model = ExternalSupplierCode
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("legal_name", "tax_id", "organization", "status")
    list_filter = ("status", "country_code", "organization")
    search_fields = ("legal_name", "trade_name", "tax_id")
    autocomplete_fields = ("organization", "created_by")
    inlines = (SupplierContactInline, SupplierCategoryInline, ExternalSupplierCodeInline)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "organization", "parent", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("code", "name")
    autocomplete_fields = ("organization", "parent")

# Register your models here.
