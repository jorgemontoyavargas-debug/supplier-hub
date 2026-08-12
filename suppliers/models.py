from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDTimeStampedModel


class Category(UUIDTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="categories",
    )
    code = models.CharField(max_length=50)
    name = models.CharField(_("nombre"), max_length=200)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "code"), name="unique_category_code_per_org"
            )
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Supplier(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Borrador")
        INVITED = "invited", _("Invitado")
        ACTIVE = "active", _("Activo")
        SUSPENDED = "suspended", _("Suspendido")
        ARCHIVED = "archived", _("Archivado")

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    legal_name = models.CharField(_("razón social"), max_length=250)
    trade_name = models.CharField(_("nombre comercial"), max_length=250, blank=True)
    tax_id = models.CharField(_("identificación fiscal"), max_length=64)
    country_code = models.CharField(_("país"), max_length=2, default="CO")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_suppliers",
    )
    categories = models.ManyToManyField(
        Category, through="SupplierCategory", related_name="suppliers"
    )

    class Meta:
        ordering = ("legal_name",)
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "tax_id"), name="unique_supplier_tax_id_per_org"
            )
        ]

    def __str__(self):
        return self.legal_name


class SupplierCategory(UUIDTimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("supplier", "category"), name="unique_supplier_category"
            )
        ]


class SupplierContact(UUIDTimeStampedModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(_("nombres"), max_length=120)
    last_name = models.CharField(_("apellidos"), max_length=120, blank=True)
    email = models.EmailField(_("correo electrónico"))
    phone = models.CharField(_("teléfono"), max_length=50, blank=True)
    job_title = models.CharField(_("cargo"), max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)
    portal_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_contacts",
    )

    class Meta:
        ordering = ("-is_primary", "first_name", "last_name")
        constraints = [
            models.UniqueConstraint(
                fields=("supplier", "email"), name="unique_contact_email_per_supplier"
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class ExternalSupplierCode(UUIDTimeStampedModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="external_codes"
    )
    system = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("supplier", "system", "company", "code"),
                name="unique_external_supplier_code",
            )
        ]

# Create your models here.
