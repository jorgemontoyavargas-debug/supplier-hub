from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "organization", "actor", "action", "object_type")
    list_filter = ("organization", "action", "object_type")
    search_fields = ("object_id",)
    readonly_fields = (
        "organization",
        "actor",
        "action",
        "object_type",
        "object_id",
        "data",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
