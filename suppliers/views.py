from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.models import AuditEvent
from organizations.models import Membership

from .forms import SupplierCreateForm, SupplierRegistrationForm
from .models import Supplier, SupplierInvitation


def _manageable_membership(user):
    memberships = (
        user.memberships.filter(
            is_active=True,
            role__in=(Membership.Role.ADMIN, Membership.Role.CATEGORY_MANAGER),
        )
        .select_related("organization")
    )
    if memberships.count() != 1:
        raise PermissionDenied
    return memberships.first()


@login_required
def supplier_list(request):
    memberships = request.user.memberships.filter(is_active=True)
    suppliers = Supplier.objects.filter(
        organization_id__in=memberships.values("organization_id")
    ).select_related("organization")
    return render(request, "suppliers/list.html", {"suppliers": suppliers})


@login_required
def supplier_create(request):
    membership = _manageable_membership(request.user)
    form = SupplierCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            supplier = form.save_for_organization(
                organization=membership.organization, created_by=request.user
            )
        except IntegrityError:
            form.add_error("tax_id", "Ya existe un proveedor con esta identificación.")
        else:
            AuditEvent.objects.create(
                organization=membership.organization,
                actor=request.user,
                action="supplier.created",
                object_type="supplier",
                object_id=str(supplier.id),
            )
            messages.success(request, "Proveedor creado. Ya puedes generar su invitación.")
            return redirect("supplier_detail", supplier_id=supplier.id)
    return render(request, "suppliers/create.html", {"form": form})


@login_required
def supplier_detail(request, supplier_id):
    memberships = request.user.memberships.filter(is_active=True)
    supplier = get_object_or_404(
        Supplier.objects.prefetch_related("contacts", "invitations"),
        id=supplier_id,
        organization_id__in=memberships.values("organization_id"),
    )
    return render(request, "suppliers/detail.html", {"supplier": supplier})


@login_required
def invite_supplier(request, supplier_id):
    if request.method != "POST":
        raise Http404
    manageable_memberships = request.user.memberships.filter(
        is_active=True,
        role__in=(Membership.Role.ADMIN, Membership.Role.CATEGORY_MANAGER),
    )
    supplier = get_object_or_404(
        Supplier,
        id=supplier_id,
        organization_id__in=manageable_memberships.values("organization_id"),
    )
    contact = supplier.contacts.filter(is_primary=True).first()
    if contact is None:
        messages.error(request, "El proveedor no tiene un contacto principal.")
        return redirect("supplier_detail", supplier_id=supplier.id)
    invitation, raw_token = SupplierInvitation.issue(
        supplier=supplier, email=contact.email, invited_by=request.user
    )
    supplier.status = Supplier.Status.INVITED
    supplier.save(update_fields=("status", "updated_at"))
    AuditEvent.objects.create(
        organization=supplier.organization,
        actor=request.user,
        action="supplier.invited",
        object_type="supplier_invitation",
        object_id=str(invitation.id),
        data={"supplier_id": str(supplier.id), "email": invitation.email},
    )
    invitation_url = request.build_absolute_uri(
        f"/proveedores/invitacion/{raw_token}/"
    )
    return render(
        request,
        "suppliers/invitation_created.html",
        {"supplier": supplier, "invitation": invitation, "invitation_url": invitation_url},
    )


def accept_invitation(request, token):
    invitation = SupplierInvitation.find_valid(token)
    if invitation is None:
        return render(request, "suppliers/invitation_invalid.html", status=410)
    form = SupplierRegistrationForm(
        request.POST or None, invitation=invitation
    )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        AuditEvent.objects.create(
            organization=invitation.supplier.organization,
            actor=user,
            action="supplier.invitation_accepted",
            object_type="supplier_invitation",
            object_id=str(invitation.id),
            data={"supplier_id": str(invitation.supplier_id)},
        )
        login(request, user)
        messages.success(request, "Cuenta creada. Bienvenido a Supplier Hub.")
        return redirect("supplier_portal")
    return render(
        request,
        "suppliers/accept_invitation.html",
        {"form": form, "invitation": invitation},
    )


@login_required
def supplier_portal(request):
    contacts = request.user.supplier_contacts.select_related("supplier").prefetch_related(
        "supplier__qualification_cases"
    )
    return render(request, "suppliers/portal.html", {"contacts": contacts})

# Create your views here.
