from django.core.exceptions import ValidationError
from django.test import TestCase

from organizations.models import Organization
from suppliers.models import Supplier

from .models import QualificationCase, QualificationTemplate


class QualificationCaseTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Pyme", slug="pyme")
        self.supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor Demo",
            tax_id="900123456",
        )
        self.template = QualificationTemplate.objects.create(
            organization=self.organization, name="Homologación general"
        )

    def test_happy_path_transitions(self):
        case = QualificationCase(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
        )

        case.transition_to(QualificationCase.Status.SUBMITTED)
        case.transition_to(QualificationCase.Status.IN_REVIEW)
        case.transition_to(QualificationCase.Status.APPROVED)

        self.assertEqual(case.status, QualificationCase.Status.APPROVED)
        self.assertIsNotNone(case.submitted_at)
        self.assertIsNotNone(case.decided_at)

    def test_invalid_transition_is_rejected(self):
        case = QualificationCase(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
        )

        with self.assertRaisesMessage(ValidationError, "Transición no permitida"):
            case.transition_to(QualificationCase.Status.APPROVED)

    def test_cross_organization_references_are_rejected(self):
        other_organization = Organization.objects.create(name="Otra", slug="otra")
        case = QualificationCase(
            organization=other_organization,
            supplier=self.supplier,
            template=self.template,
        )

        with self.assertRaises(ValidationError):
            case.full_clean()


# Create your tests here.
