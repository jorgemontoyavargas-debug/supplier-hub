import shutil
import tempfile
from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from core.models import AuditEvent, Notification
from organizations.models import Membership, Organization
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
                f"requirement_{self.document_requirement.id}_issued_at": "2026-01-01",
                f"requirement_{self.document_requirement.id}_expires_at": "2027-01-01",
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
        self.assertEqual(case.documents.get().expires_at.isoformat(), "2027-01-01")
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


class QualificationReviewTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Pyme", slug="review-pyme")
        self.supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor Revisado",
            tax_id="900456789",
        )
        self.template = QualificationTemplate.objects.create(
            organization=self.organization, name="Plantilla"
        )
        self.case = QualificationCase.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
            status=QualificationCase.Status.SUBMITTED,
        )
        self.approver = User.objects.create_user(
            username="approver", email="approver@example.test", password="approve-pass-123"
        )
        Membership.objects.create(
            user=self.approver,
            organization=self.organization,
            role=Membership.Role.APPROVER,
        )
        self.reviewer = User.objects.create_user(
            username="reviewer", email="reviewer@example.test", password="review-pass-123"
        )
        Membership.objects.create(
            user=self.reviewer,
            organization=self.organization,
            role=Membership.Role.REVIEWER,
        )

    def test_approver_can_start_review_and_approve_with_validity(self):
        self.client.force_login(self.approver)
        url = reverse("review_case", args=(self.case.id,))

        start_response = self.client.post(url, {"action": "start_review"})
        self.assertRedirects(start_response, url)
        valid_until = date.today() + timedelta(days=365)
        decision_response = self.client.post(
            url,
            {
                "action": "approved",
                "comment": "Documentación completa y vigente.",
                "valid_until": valid_until.isoformat(),
            },
        )

        self.assertRedirects(decision_response, url)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, QualificationCase.Status.APPROVED)
        self.assertEqual(self.case.valid_until, valid_until)
        self.assertEqual(self.case.reviews.count(), 1)

    def test_reviewer_can_request_changes_but_cannot_approve(self):
        self.case.status = QualificationCase.Status.IN_REVIEW
        self.case.save(update_fields=("status",))
        self.client.force_login(self.reviewer)
        url = reverse("review_case", args=(self.case.id,))

        forbidden = self.client.post(
            url,
            {
                "action": "approved",
                "comment": "No debería poder.",
                "valid_until": (date.today() + timedelta(days=30)).isoformat(),
            },
        )
        self.assertEqual(forbidden.status_code, 403)

        allowed = self.client.post(
            url,
            {"action": "changes_requested", "comment": "Actualiza el certificado."},
        )
        self.assertRedirects(allowed, url)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, QualificationCase.Status.CHANGES_REQUESTED)


class ExpirationCommandTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_command_is_idempotent_and_expires_cases(self):
        organization = Organization.objects.create(name="Pyme", slug="expiry-pyme")
        buyer = User.objects.create_user(
            username="buyer-expiry", email="buyer-expiry@example.test", password="pass-12345"
        )
        Membership.objects.create(
            user=buyer,
            organization=organization,
            role=Membership.Role.APPROVER,
        )
        supplier_user = User.objects.create_user(
            username="supplier-expiry",
            email="supplier-expiry@example.test",
            password="pass-12345",
        )
        supplier = Supplier.objects.create(
            organization=organization, legal_name="Proveedor", tax_id="800987654"
        )
        SupplierContact.objects.create(
            supplier=supplier,
            first_name="Sofía",
            email=supplier_user.email,
            portal_user=supplier_user,
        )
        template = QualificationTemplate.objects.create(
            organization=organization, name="Plantilla"
        )
        requirement = Requirement.objects.create(
            template=template,
            code="documento",
            label="Documento",
            kind=Requirement.Kind.DOCUMENT,
        )
        case = QualificationCase.objects.create(
            organization=organization,
            supplier=supplier,
            template=template,
            status=QualificationCase.Status.APPROVED,
            valid_until=date.today() - timedelta(days=1),
        )
        EvidenceDocument.objects.create(
            case=case,
            requirement=requirement,
            file=SimpleUploadedFile("vigencia.pdf", b"synthetic"),
            original_filename="vigencia.pdf",
            expires_at=date.today() + timedelta(days=10),
            uploaded_by=supplier_user,
        )

        call_command("process_expirations")
        call_command("process_expirations")

        case.refresh_from_db()
        self.assertEqual(case.status, QualificationCase.Status.EXPIRED)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(
            AuditEvent.objects.filter(
                action="qualification.expired", object_id=str(case.id)
            ).count(),
            1,
        )


# Create your tests here.
