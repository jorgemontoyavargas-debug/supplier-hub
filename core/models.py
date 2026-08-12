import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("creado"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado"), auto_now=True)

    class Meta:
        abstract = True


class AuditEvent(models.Model):
    """Evento append-only producido por una acción sensible del dominio."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    data = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-occurred_at",)
        indexes = [
            models.Index(fields=("organization", "object_type", "object_id")),
            models.Index(fields=("organization", "occurred_at")),
        ]

    def __str__(self):
        return f"{self.action}: {self.object_type}/{self.object_id}"

# Create your models here.
