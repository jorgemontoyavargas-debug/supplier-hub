from django.contrib import admin

from .models import AuditEvent, Notification


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


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "recipient", "kind", "title", "read_at")
    list_filter = ("kind", "organization")
    search_fields = ("title", "body")


# Register your models here.
