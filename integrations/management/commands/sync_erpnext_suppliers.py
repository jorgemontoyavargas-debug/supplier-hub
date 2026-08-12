import json
import os

from django.core.management.base import BaseCommand, CommandError

from integrations.adapters.erpnext import ERPNextClient, supplier_to_erpnext
from organizations.models import Organization
from suppliers.models import ExternalSupplierCode, Supplier


class Command(BaseCommand):
    help = "Muestra o aplica la sincronización de proveedores hacia ERPNext."

    def add_arguments(self, parser):
        parser.add_argument("--organization", required=True)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        try:
            organization = Organization.objects.get(slug=options["organization"])
        except Organization.DoesNotExist as error:
            raise CommandError("Organización no encontrada.") from error
        suppliers = Supplier.objects.filter(
            organization=organization,
            status__in=(Supplier.Status.ACTIVE, Supplier.Status.INVITED),
        ).prefetch_related("external_codes")

        if not options["apply"]:
            for supplier in suppliers:
                self.stdout.write(json.dumps(supplier_to_erpnext(supplier), ensure_ascii=False))
            self.stdout.write("Modo simulación. Usa --apply para enviar.")
            return

        required = ("ERPNEXT_BASE_URL", "ERPNEXT_API_KEY", "ERPNEXT_API_SECRET")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise CommandError(f"Faltan variables: {', '.join(missing)}")
        client = ERPNextClient(
            base_url=os.environ["ERPNEXT_BASE_URL"],
            api_key=os.environ["ERPNEXT_API_KEY"],
            api_secret=os.environ["ERPNEXT_API_SECRET"],
        )
        company = os.getenv("ERPNEXT_COMPANY", "")
        synced = 0
        for supplier in suppliers:
            external = supplier.external_codes.filter(
                system="erpnext", company=company
            ).first()
            result = client.upsert_supplier(
                payload=supplier_to_erpnext(supplier),
                remote_name=external.code if external else None,
            )
            remote_name = result.get("name")
            if remote_name and external is None:
                ExternalSupplierCode.objects.create(
                    supplier=supplier,
                    system="erpnext",
                    company=company,
                    code=remote_name,
                )
            synced += 1
        self.stdout.write(self.style.SUCCESS(f"Proveedores sincronizados: {synced}."))
