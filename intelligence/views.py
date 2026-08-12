from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from core.models import AuditEvent
from qualifications.models import EvidenceDocument, QualificationCase

from .models import AISuggestion
from .services import analyze_document, qualification_summary, resolve_suggestion


def _can_access_case(user, case):
    return case.supplier.contacts.filter(portal_user=user).exists() or user.memberships.filter(
        organization=case.organization, is_active=True
    ).exists()


@login_required
def case_assistance(request, case_id):
    case = get_object_or_404(
        QualificationCase.objects.select_related("supplier", "organization", "template"),
        id=case_id,
    )
    if not _can_access_case(request.user, case):
        raise PermissionDenied
    return render(
        request,
        "intelligence/case_assistance.html",
        {
            "case": case,
            "summary": qualification_summary(case),
            "documents": case.documents.prefetch_related("ai_runs__suggestions"),
        },
    )


@login_required
def analyze_evidence(request, document_id):
    if request.method != "POST":
        raise PermissionDenied
    document = get_object_or_404(
        EvidenceDocument.objects.select_related("case", "case__organization", "case__supplier"),
        id=document_id,
    )
    if not _can_access_case(request.user, document.case):
        raise PermissionDenied
    run = analyze_document(document=document, requested_by=request.user)
    AuditEvent.objects.create(
        organization=document.case.organization,
        actor=request.user,
        action="ai.document_analyzed",
        object_type="ai_analysis_run",
        object_id=str(run.id),
        data={"status": run.status, "provider": run.provider, "model": run.model_name},
    )
    if run.status == run.Status.COMPLETED:
        messages.success(request, f"Análisis completado: {run.suggestions.count()} propuestas.")
    else:
        messages.error(request, f"No fue posible analizar el documento: {run.error}")
    return redirect("case_assistance", case_id=document.case_id)


@login_required
def resolve_ai_suggestion(request, suggestion_id):
    if request.method != "POST":
        raise PermissionDenied
    suggestion = get_object_or_404(
        AISuggestion.objects.select_related(
            "run", "run__case", "run__case__organization", "run__case__supplier"
        ),
        id=suggestion_id,
    )
    if not _can_access_case(request.user, suggestion.run.case):
        raise PermissionDenied
    accept = request.POST.get("decision") == "accept"
    try:
        resolve_suggestion(suggestion=suggestion, user=request.user, accept=accept)
    except (ValidationError, ValueError) as error:
        messages.error(request, "; ".join(getattr(error, "messages", [str(error)])))
    else:
        AuditEvent.objects.create(
            organization=suggestion.run.case.organization,
            actor=request.user,
            action="ai.suggestion_accepted" if accept else "ai.suggestion_rejected",
            object_type="ai_suggestion",
            object_id=str(suggestion.id),
        )
        messages.success(request, "Propuesta resuelta.")
    return redirect("case_assistance", case_id=suggestion.run.case_id)

# Create your views here.
