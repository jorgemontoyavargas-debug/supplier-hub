from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command

from accounts.models import User
from organizations.models import Membership, Organization


class PublicViewsTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "supplier-hub")
        self.assertEqual(response.json()["database"], "ok")

    def test_home_is_available_in_spanish(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Proveedores en regla")
        self.assertContains(response, "no requiere una suscripción")


class DashboardTests(TestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_lists_only_current_users_memberships(self):
        user = User.objects.create_user(
            username="compras", email="compras@example.test", password="secret-demo"
        )
        other = User.objects.create_user(
            username="otro", email="otro@example.test", password="secret-demo"
        )
        own_organization = Organization.objects.create(name="Pyme Demo", slug="pyme-demo")
        other_organization = Organization.objects.create(name="Otra Empresa", slug="otra")
        Membership.objects.create(
            user=user,
            organization=own_organization,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            user=other,
            organization=other_organization,
            role=Membership.Role.ADMIN,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Pyme Demo")
        self.assertNotContains(response, "Otra Empresa")

    def test_supplier_user_sees_portal_but_not_buyer_navigation(self):
        from suppliers.models import Supplier, SupplierContact

        user = User.objects.create_user(
            username="portal", email="portal@example.test", password="portal-pass-123"
        )
        organization = Organization.objects.create(name="Comprador", slug="buyer-nav")
        supplier = Supplier.objects.create(
            organization=organization, legal_name="Proveedor", tax_id="900100200"
        )
        SupplierContact.objects.create(
            supplier=supplier,
            first_name="Portal",
            email=user.email,
            portal_user=user,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Mi portal")
        self.assertNotContains(response, ">Integraciones</a>")
        self.assertNotContains(response, ">Revisiones</a>")


class DemoDataTests(TestCase):
    def test_seed_command_is_idempotent(self):
        call_command("seed_demo", verbosity=0)
        call_command("seed_demo", verbosity=0)

        self.assertEqual(User.objects.filter(username="admin.demo").count(), 1)
        self.assertEqual(Organization.objects.filter(slug="pyme-demo").count(), 1)

# Create your tests here.
