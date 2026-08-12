from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from qualifications.models import EvidenceDocument, QualificationCase, Requirement

from .document_processing import extract_pages
from .models import AIAnalysisRun, AISuggestion
from .providers import configured_provider


ALLOWED_FIELDS = {"supplier.tax_id", "document.expires_at"}


@transaction.atomic
def analyze_document(*, document, requested_by):
    provider = configured_provider()
    run = AIAnalysisRun.objects.create(
        organization=document.case.organization,
        case=document.case,
        document=document,
        requested_by=requested_by,
        provider=provider.name,
        model_name=provider.model_name,
        status=AIAnalysisRun.Status.RUNNING,
    )
    try:
        pages = extract_pages(document.file.path)
        proposals = provider.analyze(pages=pages, allowed_fields=ALLOWED_FIELDS)
        for proposal in proposals:
            if not 0 <= proposal.confidence <= 1:
                continue
            AISuggestion.objects.create(
                run=run,
                field_code=proposal.field_code,
                proposed_value={"value": proposal.value},
                confidence=proposal.confidence,
                evidence_text=proposal.evidence,
                page_number=proposal.page_number,
            )
        run.status = AIAnalysisRun.Status.COMPLETED
        run.save(update_fields=("status", "updated_at"))
    except Exception as error:
        run.status = AIAnalysisRun.Status.FAILED
        run.error = str(error)[:4000]
        run.save(update_fields=("status", "error", "updated_at"))
    return run


@transaction.atomic
def resolve_suggestion(*, suggestion, user, accept):
    if suggestion.status != AISuggestion.Status.PENDING:
        raise ValidationError("La propuesta ya fue resuelta.")
    if accept:
        value = suggestion.proposed_value.get("value")
        if suggestion.field_code == "document.expires_at":
            suggestion.run.document.expires_at = date.fromisoformat(value)
            suggestion.run.document.full_clean()
            suggestion.run.document.save(update_fields=("expires_at", "updated_at"))
        elif suggestion.field_code == "supplier.tax_id":
            suggestion.run.case.supplier.tax_id = str(value)
            suggestion.run.case.supplier.full_clean()
            suggestion.run.case.supplier.save(update_fields=("tax_id", "updated_at"))
        else:
            raise ValidationError("Campo de propuesta no soportado.")
        suggestion.status = AISuggestion.Status.ACCEPTED
    else:
        suggestion.status = AISuggestion.Status.REJECTED
    suggestion.resolved_by = user
    suggestion.resolved_at = timezone.now()
    suggestion.save(
        update_fields=("status", "resolved_by", "resolved_at", "updated_at")
    )
    return suggestion


def qualification_summary(case: QualificationCase):
    category_ids = case.supplier.categories.values("id")
    requirements = case.template.requirements.filter(
        Q(category__isnull=True) | Q(category_id__in=category_ids)
    ).distinct()
    response_ids = set(case.responses.values_list("requirement_id", flat=True))
    document_ids = set(case.documents.values_list("requirement_id", flat=True))
    missing = []
    for requirement in requirements.filter(is_required=True):
        present = (
            requirement.id in document_ids
            if requirement.kind == Requirement.Kind.DOCUMENT
            else requirement.id in response_ids
        )
        if not present:
            missing.append(requirement.label)
    expiring_documents = case.documents.filter(
        expires_at__isnull=False,
        expires_at__lte=timezone.localdate() + timedelta(days=30),
    ).count()
    actions = [
        {"kind": "request_requirement", "label": f"Solicitar: {label}"}
        for label in missing
    ]
    if expiring_documents:
        actions.append(
            {
                "kind": "renew_documents",
                "label": f"Renovar {expiring_documents} documento(s) próximo(s) a vencer",
            }
        )
    pending_suggestions = AISuggestion.objects.filter(
        run__case=case, status=AISuggestion.Status.PENDING
    ).count()
    if pending_suggestions:
        actions.append(
            {
                "kind": "review_ai_suggestions",
                "label": f"Revisar {pending_suggestions} propuesta(s) automáticas",
            }
        )
    return {
        "total_requirements": requirements.count(),
        "missing": missing,
        "expiring_documents": expiring_documents,
        "pending_suggestions": pending_suggestions,
        "actions": actions,
    }
