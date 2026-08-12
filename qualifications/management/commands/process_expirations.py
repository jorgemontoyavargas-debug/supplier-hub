from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import AuditEvent, Notification
from organizations.models import Membership
from qualifications.models import EvidenceDocument, QualificationCase


class Command(BaseCommand):
    help = "Genera alertas idempotentes y vence homologaciones cuya vigencia terminó."

    def handle(self, *args, **options):
        today = timezone.localdate()
        horizon = today + timedelta(days=30)
        notifications_created = 0
        cases_expired = 0

        documents = EvidenceDocument.objects.filter(
            expires_at__isnull=False,
            expires_at__lte=horizon,
        ).select_related("case", "case__organization", "case__supplier")

        for document in documents:
            recipients = set(
                document.case.organization.memberships.filter(
                    is_active=True,
                    role__in=(
                        Membership.Role.ADMIN,
                        Membership.Role.REVIEWER,
                        Membership.Role.APPROVER,
                    ),
                ).values_list("user_id", flat=True)
            )
            recipients.update(
                document.case.supplier.contacts.exclude(portal_user=None).values_list(
                    "portal_user_id", flat=True
                )
            )
            kind = "document_expired" if document.expires_at < today else "document_expiring"
            for recipient_id in recipients:
                _, created = Notification.objects.get_or_create(
                    deduplication_key=(
                        f"{kind}:{document.id}:{document.expires_at}:{recipient_id}"
                    ),
                    defaults={
                        "organization": document.case.organization,
                        "recipient_id": recipient_id,
                        "kind": kind,
                        "title": f"Documento de {document.case.supplier.legal_name}",
                        "body": f"{document.original_filename} vence el {document.expires_at}.",
                    },
                )
                notifications_created += int(created)

        expiring_cases = QualificationCase.objects.filter(
            status__in=(
                QualificationCase.Status.APPROVED,
                QualificationCase.Status.CONDITIONAL,
            ),
            valid_until__lt=today,
        ).select_related("organization")
        for case in expiring_cases:
            case.transition_to(QualificationCase.Status.EXPIRED)
            case.save(update_fields=("status", "updated_at"))
            AuditEvent.objects.create(
                organization=case.organization,
                action="qualification.expired",
                object_type="qualification_case",
                object_id=str(case.id),
                data={"valid_until": case.valid_until.isoformat()},
            )
            cases_expired += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Alertas creadas: {notifications_created}. Expedientes vencidos: {cases_expired}."
            )
        )
