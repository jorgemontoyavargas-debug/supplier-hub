from django.contrib import admin

from .models import APICredential, IdempotencyRecord, WebhookDelivery, WebhookSubscription


@admin.register(APICredential)
class APICredentialAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "key_prefix", "is_active", "last_used_at")
    readonly_fields = ("key_prefix", "key_hash", "last_used_at")


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "url", "is_active")
    list_filter = ("organization", "is_active")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("event_type", "subscription", "status", "attempts", "created_at")
    list_filter = ("status", "event_type")
    readonly_fields = (
        "subscription",
        "event_id",
        "event_type",
        "payload",
        "status",
        "attempts",
        "next_attempt_at",
        "delivered_at",
        "last_error",
    )


@admin.register(IdempotencyRecord)
class IdempotencyRecordAdmin(admin.ModelAdmin):
    list_display = ("organization", "endpoint", "key", "status_code", "created_at")
    readonly_fields = (
        "organization",
        "key",
        "endpoint",
        "request_hash",
        "status_code",
        "response_body",
    )

# Register your models here.
