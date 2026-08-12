from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from core.models import UUIDTimeStampedModel


class AIAnalysisRun(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        RUNNING = "running", "Ejecutando"
        COMPLETED = "completed", "Completado"
        FAILED = "failed", "Fallido"

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="ai_runs"
    )
    case = models.ForeignKey(
        "qualifications.QualificationCase",
        on_delete=models.CASCADE,
        related_name="ai_runs",
    )
    document = models.ForeignKey(
        "qualifications.EvidenceDocument",
        on_delete=models.CASCADE,
        related_name="ai_runs",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_ai_runs",
    )
    provider = models.CharField(max_length=80)
    model_name = models.CharField(max_length=120)
    prompt_version = models.CharField(max_length=40, default="document-v1")
    status = models.CharField(max_length=20, choices=Status.choices)
    error = models.TextField(blank=True)


class AISuggestion(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        ACCEPTED = "accepted", "Aceptada"
        REJECTED = "rejected", "Rechazada"

    run = models.ForeignKey(AIAnalysisRun, on_delete=models.CASCADE, related_name="suggestions")
    field_code = models.CharField(max_length=200)
    proposed_value = models.JSONField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    evidence_text = models.TextField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_ai_suggestions",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-confidence", "field_code")
