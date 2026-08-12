from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.models import AuditEvent
from organizations.models import Membership
from suppliers.models import Supplier

from .models import (
    EvidenceDocument,
    QualificationCase,
    QualificationTemplate,
    Requirement,
    RequirementResponse,
)

ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx"}
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024


def _supplier_for_portal_user(user, supplier_id):
    return get_object_or_404(
        Supplier.objects.select_related("organization"),
        id=supplier_id,
        contacts__portal_user=user,
    )


def _can_access_case(user, case):
    if case.supplier.contacts.filter(portal_user=user).exists():
        return True
    return user.memberships.filter(
        organization=case.organization, is_active=True
    ).exists()


def _requirements_for(case):
    category_ids = case.supplier.categories.values("id")
    return case.template.requirements.filter(
        Q(category__isnull=True) | Q(category_id__in=category_ids)
    ).distinct()


@login_required
def start_case(request, supplier_id):
    if request.method != "POST":
        raise PermissionDenied
    supplier = _supplier_for_portal_user(request.user, supplier_id)
    template = (
        QualificationTemplate.objects.filter(
            organization=supplier.organization, is_active=True
        )
        .order_by("name", "-version")
        .first()
    )
    if template is None:
        messages.error(request, "La empresa compradora aún no configuró una homologación.")
        return redirect("supplier_portal")
    case, created = QualificationCase.objects.get_or_create(
        supplier=supplier,
        template=template,
        defaults={"organization": supplier.organization},
    )
    if created:
        AuditEvent.objects.create(
            organization=case.organization,
            actor=request.user,
            action="qualification.started",
            object_type="qualification_case",
            object_id=str(case.id),
        )
    return redirect("qualification_case", case_id=case.id)


def _validate_upload(upload):
    extension = Path(upload.name).suffix.lower()
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError("Tipo de archivo no permitido.")
    if upload.size > MAX_DOCUMENT_SIZE:
        raise ValidationError("El archivo supera el límite de 10 MB.")


@login_required
@transaction.atomic
def qualification_case(request, case_id):
    case = get_object_or_404(
        QualificationCase.objects.select_related(
            "organization", "supplier", "template"
        ),
        id=case_id,
    )
    if not _can_access_case(request.user, case):
        raise PermissionDenied
    requirements = list(_requirements_for(case))
    existing = {
        response.requirement_id: response
        for response in case.responses.filter(requirement__in=requirements)
    }
    errors = []
    if request.method == "POST":
        if case.status not in {
            QualificationCase.Status.DRAFT,
            QualificationCase.Status.CHANGES_REQUESTED,
        }:
            raise PermissionDenied
        for requirement in requirements:
            key = f"requirement_{requirement.id}"
            if requirement.kind == Requirement.Kind.DOCUMENT:
                upload = request.FILES.get(key)
                if upload:
                    try:
                        _validate_upload(upload)
                    except ValidationError as error:
                        errors.extend(error.messages)
                    else:
                        current_version = (
                            case.documents.filter(requirement=requirement)
                            .order_by("-version")
                            .values_list("version", flat=True)
                            .first()
                            or 0
                        )
                        EvidenceDocument.objects.create(
                            case=case,
                            requirement=requirement,
                            file=upload,
                            original_filename=Path(upload.name).name,
                            version=current_version + 1,
                            uploaded_by=request.user,
                        )
                if requirement.is_required and not case.documents.filter(
                    requirement=requirement
                ).exists():
                    errors.append(f"Falta el documento: {requirement.label}.")
                continue

            raw_value = request.POST.get(key, "").strip()
            if requirement.is_required and not raw_value:
                errors.append(f"Falta responder: {requirement.label}.")
                continue
            RequirementResponse.objects.update_or_create(
                case=case,
                requirement=requirement,
                defaults={"value": {"value": raw_value}},
            )

        if not errors and request.POST.get("action") == "submit":
            case.transition_to(QualificationCase.Status.SUBMITTED)
            case.full_clean()
            case.save()
            AuditEvent.objects.create(
                organization=case.organization,
                actor=request.user,
                action="qualification.submitted",
                object_type="qualification_case",
                object_id=str(case.id),
            )
            messages.success(request, "Expediente enviado para revisión.")
            return redirect("qualification_case", case_id=case.id)
        if not errors:
            messages.success(request, "Borrador guardado.")
            return redirect("qualification_case", case_id=case.id)

    documents = {document.requirement_id: document for document in case.documents.all()}
    rows = [
        {
            "requirement": requirement,
            "response": existing.get(requirement.id),
            "document": documents.get(requirement.id),
        }
        for requirement in requirements
    ]
    return render(
        request,
        "qualifications/case.html",
        {"case": case, "rows": rows, "errors": errors},
    )


@login_required
def download_evidence(request, document_id):
    document = get_object_or_404(
        EvidenceDocument.objects.select_related("case", "case__organization"),
        id=document_id,
    )
    if not _can_access_case(request.user, document.case):
        raise PermissionDenied
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.original_filename,
    )

# Create your views here.
