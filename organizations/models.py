from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDTimeStampedModel


class Organization(UUIDTimeStampedModel):
    name = models.CharField(_("nombre"), max_length=200)
    slug = models.SlugField(unique=True)
    tax_id = models.CharField(_("identificación fiscal"), max_length=64, blank=True)
    country_code = models.CharField(_("país"), max_length=2, default="CO")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Membership(UUIDTimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrador")
        CATEGORY_MANAGER = "category_manager", _("Gestor de categoría")
        REVIEWER = "reviewer", _("Revisor")
        APPROVER = "approver", _("Aprobador")
        OBSERVER = "observer", _("Observador")

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=32, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "user"), name="unique_org_membership"
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.organization} ({self.get_role_display()})"

# Create your models here.
