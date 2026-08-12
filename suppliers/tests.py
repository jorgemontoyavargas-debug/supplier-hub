from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta

from accounts.models import User
from core.models import AuditEvent
from organizations.models import Membership
from organizations.models import Organization

from .models import Supplier, SupplierContact, SupplierInvitation


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


class SupplierOnboardingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@example.test", password="admin-pass-123"
        )
        self.organization = Organization.objects.create(name="Pyme", slug="pyme")
        Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )
        self.client.force_login(self.user)

    def test_admin_can_create_supplier_and_primary_contact(self):
        response = self.client.post(
            reverse("supplier_create"),
            {
                "legal_name": "Nuevo Proveedor S.A.S.",
                "trade_name": "Nuevo Proveedor",
                "tax_id": "901234567",
                "country_code": "CO",
                "contact_first_name": "Laura",
                "contact_last_name": "Ventas",
                "contact_email": "laura@proveedor.test",
            },
        )

        supplier = Supplier.objects.get(tax_id="901234567")
        self.assertRedirects(response, reverse("supplier_detail", args=(supplier.id,)))
        self.assertTrue(
            SupplierContact.objects.filter(
                supplier=supplier,
                email="laura@proveedor.test",
                is_primary=True,
            ).exists()
        )
        self.assertTrue(
            AuditEvent.objects.filter(action="supplier.created", object_id=str(supplier.id)).exists()
        )

    def test_user_cannot_view_supplier_from_another_organization(self):
        other = Organization.objects.create(name="Otra", slug="otra")
        supplier = Supplier.objects.create(
            organization=other, legal_name="Oculto", tax_id="800000001"
        )

        response = self.client.get(reverse("supplier_detail", args=(supplier.id,)))

        self.assertEqual(response.status_code, 404)

    def test_invitation_token_is_not_stored_and_can_only_be_used_once(self):
        supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor Invitado",
            tax_id="900000099",
        )
        SupplierContact.objects.create(
            supplier=supplier,
            first_name="Mario",
            email="mario@proveedor.test",
            is_primary=True,
        )
        invitation, token = SupplierInvitation.issue(
            supplier=supplier,
            email="mario@proveedor.test",
            invited_by=self.user,
        )

        self.assertNotEqual(invitation.token_hash, token)
        self.client.logout()
        accept_url = reverse("accept_invitation", args=(token,))
        response = self.client.post(
            accept_url,
            {
                "first_name": "Mario",
                "last_name": "Proveedor",
                "password1": "a-strong-demo-password-493",
                "password2": "a-strong-demo-password-493",
            },
        )

        self.assertRedirects(response, reverse("supplier_portal"))
        invitation.refresh_from_db()
        supplier.refresh_from_db()
        self.assertIsNotNone(invitation.accepted_at)
        self.assertEqual(supplier.status, Supplier.Status.ACTIVE)
        self.assertIsNotNone(
            SupplierContact.objects.get(
                supplier=supplier, email="mario@proveedor.test"
            ).portal_user
        )

        second_response = self.client.get(accept_url)
        self.assertEqual(second_response.status_code, 410)

    def test_expired_invitation_is_rejected(self):
        supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor Vencido",
            tax_id="900000100",
        )
        invitation, token = SupplierInvitation.issue(
            supplier=supplier,
            email="vencido@proveedor.test",
            invited_by=self.user,
            lifetime=timedelta(seconds=-1),
        )
        self.assertLess(invitation.expires_at, timezone.now())
        self.client.logout()

        response = self.client.get(reverse("accept_invitation", args=(token,)))

        self.assertEqual(response.status_code, 410)

    def test_observer_cannot_create_a_supplier(self):
        observer = User.objects.create_user(
            username="observer", email="observer@example.test", password="observer-pass-123"
        )
        Membership.objects.create(
            user=observer,
            organization=self.organization,
            role=Membership.Role.OBSERVER,
        )
        self.client.force_login(observer)

        response = self.client.get(reverse("supplier_create"))

        self.assertEqual(response.status_code, 403)

# Create your tests here.
