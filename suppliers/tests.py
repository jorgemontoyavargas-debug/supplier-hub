from django.db import IntegrityError, transaction
from django.test import TestCase

from organizations.models import Organization

from .models import Supplier


class SupplierIsolationTests(TestCase):
    def test_tax_id_is_unique_inside_an_organization(self):
        organization = Organization.objects.create(name="Pyme", slug="pyme")
        Supplier.objects.create(
            organization=organization, legal_name="Proveedor Uno", tax_id="900123456"
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Supplier.objects.create(
                organization=organization,
                legal_name="Proveedor Duplicado",
                tax_id="900123456",
            )

    def test_same_tax_id_can_exist_in_different_organizations(self):
        first = Organization.objects.create(name="Primera", slug="primera")
        second = Organization.objects.create(name="Segunda", slug="segunda")

        Supplier.objects.create(
            organization=first, legal_name="Proveedor", tax_id="900123456"
        )
        Supplier.objects.create(
            organization=second, legal_name="Proveedor", tax_id="900123456"
        )

        self.assertEqual(Supplier.objects.count(), 2)

# Create your tests here.
