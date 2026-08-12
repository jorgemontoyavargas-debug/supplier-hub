import csv
import io
import json
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from organizations.models import Membership, Organization
from suppliers.models import Supplier

from .models import APICredential, WebhookDelivery, WebhookSubscription
from .services import publish_event
from .adapters.erpnext import supplier_to_erpnext


class SupplierAPITests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Pyme API", slug="pyme-api")
        self.credential, self.raw_key = APICredential.issue(
            organization=self.organization, name="ERP"
        )
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.raw_key}"}

    def test_key_is_hashed_and_authentication_is_required(self):
        self.assertNotEqual(self.credential.key_hash, self.raw_key)
        response = self.client.get(reverse("api_suppliers"))
        self.assertEqual(response.status_code, 401)

    def test_upsert_is_idempotent_and_scoped_to_organization(self):
        other = Organization.objects.create(name="Otra API", slug="otra-api")
        Supplier.objects.create(
            organization=other, legal_name="Proveedor Oculto", tax_id="800000000"
        )
        payload = {
            "legal_name": "Proveedor Integrado S.A.S.",
            "tax_id": "901888777",
            "country_code": "CO",
            "external_code": {"system": "erpnext", "company": "ACME", "code": "SUP-001"},
        }
        response = self.client.post(
            reverse("api_suppliers"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="request-001",
            **self.headers,
        )
        repeated = self.client.post(
            reverse("api_suppliers"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="request-001",
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(repeated.status_code, 201)
        self.assertEqual(response.json(), repeated.json())
        self.assertEqual(Supplier.objects.filter(organization=self.organization).count(), 1)
        self.assertEqual(
            response.json()["data"]["external_codes"][0]["code"], "SUP-001"
        )
        listed = self.client.get(reverse("api_suppliers"), **self.headers)
        self.assertEqual(len(listed.json()["data"]), 1)
        self.assertEqual(listed.json()["data"][0]["tax_id"], "901888777")

    def test_reusing_key_with_different_payload_is_conflict(self):
        first = {"legal_name": "Uno", "tax_id": "1"}
        second = {"legal_name": "Dos", "tax_id": "2"}
        url = reverse("api_suppliers")
        self.client.post(
            url,
            data=json.dumps(first),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="same-key",
            **self.headers,
        )

        response = self.client.post(
            url,
            data=json.dumps(second),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="same-key",
            **self.headers,
        )

        self.assertEqual(response.status_code, 409)


class SupplierCSVTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Pyme CSV", slug="pyme-csv")
        self.user = User.objects.create_user(
            username="csv-admin", email="csv@example.test", password="csv-pass-123"
        )
        Membership.objects.create(
            organization=self.organization,
            user=self.user,
            role=Membership.Role.ADMIN,
        )
        self.client.force_login(self.user)

    def test_import_and_export_csv(self):
        content = (
            "tax_id,legal_name,trade_name,country_code,external_system,external_company,external_code\n"
            "900111222,Proveedor CSV,Proveedor,CO,erpnext,ACME,SUP-CSV\n"
        ).encode("utf-8")
        response = self.client.post(
            reverse("supplier_csv"),
            {"file": SimpleUploadedFile("proveedores.csv", content, content_type="text/csv")},
        )
        self.assertRedirects(response, reverse("supplier_csv"))
        self.assertTrue(Supplier.objects.filter(tax_id="900111222").exists())

        exported = self.client.get(reverse("supplier_csv") + "?download=1")
        rows = list(csv.DictReader(io.StringIO(exported.content.decode("utf-8-sig"))))
        self.assertEqual(rows[0]["legal_name"], "Proveedor CSV")
        self.assertEqual(rows[0]["external_code"], "SUP-CSV")


class WebhookTests(TestCase):
    @patch("integrations.management.commands.deliver_webhooks.urlopen")
    def test_event_is_signed_and_delivered_once(self, urlopen):
        organization = Organization.objects.create(name="Pyme Hook", slug="pyme-hook")
        subscription = WebhookSubscription.objects.create(
            organization=organization,
            name="ERP",
            url="https://erp.example.test/hooks/supplier-hub",
            secret="shared-test-secret",
            event_types=["supplier.created"],
        )
        publish_event(
            organization=organization,
            event_type="supplier.created",
            data={"id": "supplier-1"},
        )
        mocked_response = MagicMock()
        mocked_response.status = 204
        mocked_response.__enter__.return_value = mocked_response
        urlopen.return_value = mocked_response

        call_command("deliver_webhooks")
        call_command("deliver_webhooks")

        delivery = WebhookDelivery.objects.get(subscription=subscription)
        self.assertEqual(delivery.status, WebhookDelivery.Status.DELIVERED)
        self.assertEqual(delivery.attempts, 1)
        request = urlopen.call_args.args[0]
        self.assertTrue(request.headers["X-supplierhub-signature"].startswith("v1="))
        self.assertEqual(urlopen.call_count, 1)


class ERPNextAdapterTests(TestCase):
    def test_supplier_mapping_uses_only_standard_fields(self):
        organization = Organization.objects.create(name="Pyme ERP", slug="pyme-erp")
        supplier = Supplier.objects.create(
            organization=organization,
            legal_name="Proveedor ERP S.A.S.",
            tax_id="901333222",
            country_code="CO",
        )

        self.assertEqual(
            supplier_to_erpnext(supplier),
            {
                "supplier_name": "Proveedor ERP S.A.S.",
                "supplier_type": "Company",
                "tax_id": "901333222",
                "country": "CO",
            },
        )

# Create your tests here.
