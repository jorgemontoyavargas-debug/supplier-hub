import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from core.models import AuditEvent
from organizations.models import Organization
from suppliers.models import Supplier, SupplierContact

from .models import EvidenceDocument, QualificationCase, QualificationTemplate, Requirement


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


class SupplierQualificationJourneyTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.organization = Organization.objects.create(name="Pyme", slug="pyme")
        self.user = User.objects.create_user(
            username="proveedor@example.test",
            email="proveedor@example.test",
            password="supplier-pass-398",
        )
        self.supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor Portal",
            tax_id="900700800",
            status=Supplier.Status.ACTIVE,
        )
        SupplierContact.objects.create(
            supplier=self.supplier,
            first_name="Paula",
            email=self.user.email,
            portal_user=self.user,
            is_primary=True,
        )
        self.template = QualificationTemplate.objects.create(
            organization=self.organization, name="Homologación general"
        )
        self.text_requirement = Requirement.objects.create(
            template=self.template,
            code="actividad",
            label="Actividad principal",
            kind=Requirement.Kind.TEXT,
            sort_order=10,
        )
        self.document_requirement = Requirement.objects.create(
            template=self.template,
            code="certificado",
            label="Certificado legal",
            kind=Requirement.Kind.DOCUMENT,
            sort_order=20,
        )
        self.client.force_login(self.user)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_supplier_can_start_complete_and_submit_case(self):
        response = self.client.post(reverse("start_qualification", args=(self.supplier.id,)))
        case = QualificationCase.objects.get(supplier=self.supplier)
        self.assertRedirects(response, reverse("qualification_case", args=(case.id,)))

        document = SimpleUploadedFile(
            "certificado.pdf", b"%PDF-1.4 synthetic test", content_type="application/pdf"
        )
        submit_response = self.client.post(
            reverse("qualification_case", args=(case.id,)),
            {
                f"requirement_{self.text_requirement.id}": "Servicios de mantenimiento",
                f"requirement_{self.document_requirement.id}": document,
                "action": "submit",
            },
        )

        self.assertRedirects(
            submit_response, reverse("qualification_case", args=(case.id,))
        )
        case.refresh_from_db()
        self.assertEqual(case.status, QualificationCase.Status.SUBMITTED)
        self.assertEqual(case.responses.count(), 1)
        self.assertEqual(case.documents.count(), 1)
        self.assertTrue(
            AuditEvent.objects.filter(
                action="qualification.submitted", object_id=str(case.id)
            ).exists()
        )

    def test_required_answers_prevent_submission(self):
        case = QualificationCase.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
        )

        response = self.client.post(
            reverse("qualification_case", args=(case.id,)), {"action": "submit"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Falta responder")
        self.assertContains(response, "Falta el documento")
        case.refresh_from_db()
        self.assertEqual(case.status, QualificationCase.Status.DRAFT)

    def test_unrelated_user_cannot_download_document(self):
        case = QualificationCase.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
        )
        document = EvidenceDocument.objects.create(
            case=case,
            requirement=self.document_requirement,
            file=SimpleUploadedFile("certificado.pdf", b"private"),
            original_filename="certificado.pdf",
            uploaded_by=self.user,
        )
        unrelated = User.objects.create_user(
            username="intruso", email="intruso@example.test", password="intruder-pass-123"
        )
        self.client.force_login(unrelated)

        response = self.client.get(reverse("download_evidence", args=(document.id,)))

        self.assertEqual(response.status_code, 403)


# Create your tests here.
