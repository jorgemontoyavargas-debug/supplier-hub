from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import UUIDTimeStampedModel


class QualificationTemplate(UUIDTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="qualification_templates",
    )
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "name", "version"),
                name="unique_qualification_template_version",
            )
        ]

    def __str__(self):
        return f"{self.name} v{self.version}"


class Requirement(UUIDTimeStampedModel):
    class Kind(models.TextChoices):
        TEXT = "text", _("Texto")
        NUMBER = "number", _("Número")
        DATE = "date", _("Fecha")
        BOOLEAN = "boolean", _("Sí/No")
        SELECT = "select", _("Selección")
        DOCUMENT = "document", _("Documento")

    template = models.ForeignKey(
        QualificationTemplate, on_delete=models.CASCADE, related_name="requirements"
    )
    category = models.ForeignKey(
        "suppliers.Category",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="qualification_requirements",
    )
    code = models.CharField(max_length=80)
    label = models.CharField(max_length=250)
    instructions = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    is_required = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "code")
        constraints = [
            models.UniqueConstraint(
                fields=("template", "code"), name="unique_requirement_code_per_template"
            )
        ]


class QualificationCase(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Borrador")
        SUBMITTED = "submitted", _("Enviado")
        IN_REVIEW = "in_review", _("En revisión")
        CHANGES_REQUESTED = "changes_requested", _("Correcciones solicitadas")
        APPROVED = "approved", _("Aprobado")
        CONDITIONAL = "conditional", _("Condicional")
        REJECTED = "rejected", _("Rechazado")
        SUSPENDED = "suspended", _("Suspendido")
        EXPIRED = "expired", _("Vencido")

    ALLOWED_TRANSITIONS = {
        Status.DRAFT: {Status.SUBMITTED},
        Status.SUBMITTED: {Status.IN_REVIEW},
        Status.IN_REVIEW: {
            Status.CHANGES_REQUESTED,
            Status.APPROVED,
            Status.CONDITIONAL,
            Status.REJECTED,
        },
        Status.CHANGES_REQUESTED: {Status.SUBMITTED},
        Status.APPROVED: {Status.SUSPENDED, Status.EXPIRED},
        Status.CONDITIONAL: {Status.SUSPENDED, Status.EXPIRED},
        Status.SUSPENDED: {Status.IN_REVIEW},
        Status.REJECTED: set(),
        Status.EXPIRED: {Status.IN_REVIEW},
    }

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="qualification_cases",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="qualification_cases",
    )
    template = models.ForeignKey(
        QualificationTemplate,
        on_delete=models.PROTECT,
        related_name="cases",
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.DRAFT
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("supplier", "template"),
                condition=models.Q(
                    status__in=(
                        "draft",
                        "submitted",
                        "in_review",
                        "changes_requested",
                    )
                ),
                name="one_open_case_per_supplier_template",
            )
        ]

    def clean(self):
        if self.supplier_id and self.organization_id:
            if self.supplier.organization_id != self.organization_id:
                raise ValidationError("El proveedor pertenece a otra organización.")
        if self.template_id and self.organization_id:
            if self.template.organization_id != self.organization_id:
                raise ValidationError("La plantilla pertenece a otra organización.")

    def transition_to(self, target_status):
        if target_status not in self.ALLOWED_TRANSITIONS.get(self.status, set()):
            raise ValidationError(
                f"Transición no permitida: {self.status} → {target_status}."
            )
        self.status = target_status
        if target_status == self.Status.SUBMITTED:
            self.submitted_at = timezone.now()
        if target_status in {
            self.Status.APPROVED,
            self.Status.CONDITIONAL,
            self.Status.REJECTED,
        }:
            self.decided_at = timezone.now()


class RequirementResponse(UUIDTimeStampedModel):
    case = models.ForeignKey(
        QualificationCase, on_delete=models.CASCADE, related_name="responses"
    )
    requirement = models.ForeignKey(
        Requirement, on_delete=models.PROTECT, related_name="responses"
    )
    value = models.JSONField(default=dict, blank=True)
    is_accepted = models.BooleanField(null=True, blank=True)
    reviewer_comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("case", "requirement"), name="unique_response_per_requirement"
            )
        ]


def evidence_upload_path(instance, filename):
    return f"organizations/{instance.case.organization_id}/cases/{instance.case_id}/{filename}"


class EvidenceDocument(UUIDTimeStampedModel):
    case = models.ForeignKey(
        QualificationCase, on_delete=models.CASCADE, related_name="documents"
    )
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documents",
    )
    file = models.FileField(upload_to=evidence_upload_path)
    original_filename = models.CharField(max_length=255)
    issued_at = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_evidence_documents",
    )

    class Meta:
        ordering = ("-created_at",)

# Create your models here.
