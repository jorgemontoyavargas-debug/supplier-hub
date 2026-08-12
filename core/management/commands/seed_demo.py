from django.core.management.base import BaseCommand

from accounts.models import User
from organizations.models import Membership, Organization
from qualifications.models import QualificationTemplate, Requirement
from suppliers.models import Category, Supplier, SupplierContact


class Command(BaseCommand):
    help = "Crea una organización y un expediente base para demostración local."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="admin.demo",
            defaults={
                "email": "admin@supplierhub.local",
                "first_name": "Ana",
                "last_name": "Compras",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("supplierhub-demo")
            user.save(update_fields=("password",))

        organization, _ = Organization.objects.get_or_create(
            slug="pyme-demo",
            defaults={"name": "Pyme Demo S.A.S.", "tax_id": "900000001"},
        )
        Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={"role": Membership.Role.ADMIN},
        )
        category, _ = Category.objects.get_or_create(
            organization=organization,
            code="SERV-GEN",
            defaults={"name": "Servicios generales"},
        )
        supplier, _ = Supplier.objects.get_or_create(
            organization=organization,
            tax_id="901000002",
            defaults={
                "legal_name": "Proveedor Ejemplo S.A.S.",
                "trade_name": "Proveedor Ejemplo",
                "status": Supplier.Status.INVITED,
                "created_by": user,
            },
        )
        supplier.categories.add(category, through_defaults={"is_primary": True})
        SupplierContact.objects.get_or_create(
            supplier=supplier,
            email="contacto@proveedor.test",
            defaults={"first_name": "Carlos", "last_name": "Proveedor", "is_primary": True},
        )
        template, _ = QualificationTemplate.objects.get_or_create(
            organization=organization,
            name="Homologación general",
            version=1,
        )
        Requirement.objects.get_or_create(
            template=template,
            code="camara-comercio",
            defaults={
                "label": "Certificado de existencia y representación legal",
                "kind": Requirement.Kind.DOCUMENT,
                "sort_order": 10,
            },
        )
        Requirement.objects.get_or_create(
            template=template,
            code="actividad-economica",
            defaults={
                "label": "Describa la actividad económica principal",
                "kind": Requirement.Kind.TEXT,
                "sort_order": 20,
            },
        )

        self.stdout.write(self.style.SUCCESS("Datos demo creados o actualizados."))
        self.stdout.write("Usuario: admin.demo")
        self.stdout.write("Contraseña inicial: supplierhub-demo")
