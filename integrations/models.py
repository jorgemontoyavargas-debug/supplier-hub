from django.db import models

# Create your models here.
import hashlib
import secrets

from django.db import models
from django.utils import timezone

from core.models import UUIDTimeStampedModel


class APICredential(UUIDTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="api_credentials",
    )
    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=16)
    key_hash = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def hash_key(raw_key):
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def issue(cls, *, organization, name):
        raw_key = f"sh_{secrets.token_urlsafe(32)}"
        credential = cls.objects.create(
            organization=organization,
            name=name,
            key_prefix=raw_key[:12],
            key_hash=cls.hash_key(raw_key),
        )
        return credential, raw_key

    @classmethod
    def authenticate(cls, raw_key):
        try:
            credential = cls.objects.select_related("organization").get(
                key_hash=cls.hash_key(raw_key), is_active=True
            )
        except cls.DoesNotExist:
            return None
        credential.last_used_at = timezone.now()
        credential.save(update_fields=("last_used_at", "updated_at"))
        return credential


class IdempotencyRecord(UUIDTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    key = models.CharField(max_length=150)
    endpoint = models.CharField(max_length=150)
    request_hash = models.CharField(max_length=64)
    status_code = models.PositiveSmallIntegerField()
    response_body = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "key", "endpoint"),
                name="unique_idempotency_key_per_endpoint",
            )
        ]


class WebhookSubscription(UUIDTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions",
    )
    name = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=250)
    event_types = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)


class WebhookDelivery(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        DELIVERED = "delivered", "Entregado"
        FAILED = "failed", "Fallido"

    subscription = models.ForeignKey(
        WebhookSubscription, on_delete=models.CASCADE, related_name="deliveries"
    )
    event_id = models.UUIDField()
    event_type = models.CharField(max_length=120)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(default=timezone.now)
    delivered_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("subscription", "event_id"),
                name="unique_webhook_delivery_per_event",
            )
        ]
        indexes = [models.Index(fields=("status", "next_attempt_at"))]
