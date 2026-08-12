import shutil
import tempfile
from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from organizations.models import Organization
from qualifications.models import EvidenceDocument, QualificationCase, QualificationTemplate, Requirement
from suppliers.models import Supplier, SupplierContact

from .document_processing import DocumentPage
from .models import AISuggestion
from .providers import RuleBasedProvider
from .services import analyze_document, qualification_summary, resolve_suggestion


class RuleBasedProviderTests(TestCase):
    def test_extracts_tax_id_and_expiry_with_evidence(self):
        page = DocumentPage(
            number=2,
            text="Certificamos que el NIT: 901.234.567-8 tiene vigencia hasta 2027-05-31.",
        )

        proposals = RuleBasedProvider().analyze(
            pages=[page], allowed_fields={"supplier.tax_id", "document.expires_at"}
        )

        values = {item.field_code: item for item in proposals}
        self.assertEqual(values["supplier.tax_id"].value, "9012345678")
        self.assertEqual(values["document.expires_at"].value, "2027-05-31")
        self.assertEqual(values["document.expires_at"].page_number, 2)
        self.assertIn(values["document.expires_at"].evidence, page.text)


class IntelligenceJourneyTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.organization = Organization.objects.create(name="Pyme IA", slug="pyme-ia")
        self.user = User.objects.create_user(
            username="ai-supplier", email="ai@provider.test", password="ai-pass-12345"
        )
        self.supplier = Supplier.objects.create(
            organization=self.organization,
            legal_name="Proveedor IA",
            tax_id="900000001",
        )
        SupplierContact.objects.create(
            supplier=self.supplier,
            first_name="Irene",
            email=self.user.email,
            portal_user=self.user,
        )
        self.template = QualificationTemplate.objects.create(
            organization=self.organization, name="Plantilla IA"
        )
        self.requirement = Requirement.objects.create(
            template=self.template,
            code="certificado",
            label="Certificado vigente",
            kind=Requirement.Kind.DOCUMENT,
        )
        self.case = QualificationCase.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            template=self.template,
        )
        self.document = EvidenceDocument.objects.create(
            case=self.case,
            requirement=self.requirement,
            file=SimpleUploadedFile("certificado.pdf", b"synthetic"),
            original_filename="certificado.pdf",
            uploaded_by=self.user,
        )

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    @patch("intelligence.services.extract_pages")
    def test_analysis_creates_evidence_backed_suggestions(self, extract_pages):
        extract_pages.return_value = [
            DocumentPage(
                1,
                "El NIT 901.999.888-7 se encuentra vigente. Vencimiento: 2028-06-30.",
            )
        ]

        run = analyze_document(document=self.document, requested_by=self.user)

        self.assertEqual(run.status, run.Status.COMPLETED)
        self.assertEqual(run.suggestions.count(), 2)
        suggestion = run.suggestions.get(field_code="document.expires_at")
        resolve_suggestion(suggestion=suggestion, user=self.user, accept=True)
        self.document.refresh_from_db()
        self.assertEqual(self.document.expires_at, date(2028, 6, 30))
        suggestion.refresh_from_db()
        self.assertEqual(suggestion.status, AISuggestion.Status.ACCEPTED)

    def test_summary_reports_missing_requirement(self):
        self.document.delete()
        summary = qualification_summary(self.case)

        self.assertEqual(summary["total_requirements"], 1)
        self.assertEqual(summary["missing"], ["Certificado vigente"])

    def test_unrelated_user_cannot_open_assistance(self):
        unrelated = User.objects.create_user(
            username="ai-intruder", email="intruder@ai.test", password="ai-pass-98765"
        )
        self.client.force_login(unrelated)

        response = self.client.get(reverse("case_assistance", args=(self.case.id,)))

        self.assertEqual(response.status_code, 403)

# Create your tests here.
