import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from organizations.models import Membership
from suppliers.models import ExternalSupplierCode, Supplier


def _single_manageable_organization(user):
    memberships = user.memberships.filter(
        is_active=True,
        role__in=(Membership.Role.ADMIN, Membership.Role.CATEGORY_MANAGER),
    ).select_related("organization")
    if memberships.count() != 1:
        raise PermissionDenied
    return memberships.first().organization


@login_required
def supplier_csv(request):
    organization = _single_manageable_organization(request.user)
    if request.method == "GET" and request.GET.get("download") == "1":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="supplier-hub-proveedores.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(
            (
                "tax_id",
                "legal_name",
                "trade_name",
                "country_code",
                "status",
                "external_system",
                "external_company",
                "external_code",
            )
        )
        suppliers = Supplier.objects.filter(organization=organization).prefetch_related(
            "external_codes"
        )
        for supplier in suppliers:
            codes = list(supplier.external_codes.all()) or [None]
            for code in codes:
                writer.writerow(
                    (
                        supplier.tax_id,
                        supplier.legal_name,
                        supplier.trade_name,
                        supplier.country_code,
                        supplier.status,
                        code.system if code else "",
                        code.company if code else "",
                        code.code if code else "",
                    )
                )
        return response

    if request.method == "POST":
        upload = request.FILES.get("file")
        if upload is None or upload.size > 2 * 1024 * 1024:
            messages.error(request, "Selecciona un CSV de máximo 2 MB.")
            return redirect("supplier_csv")
        try:
            content = upload.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            required_headers = {"tax_id", "legal_name"}
            if not required_headers.issubset(reader.fieldnames or []):
                raise ValueError("El CSV debe incluir tax_id y legal_name.")
            count = 0
            with transaction.atomic():
                for row_number, row in enumerate(reader, start=2):
                    tax_id = (row.get("tax_id") or "").strip()
                    legal_name = (row.get("legal_name") or "").strip()
                    if not tax_id or not legal_name:
                        raise ValueError(f"Fila {row_number}: faltan tax_id o legal_name.")
                    supplier, _ = Supplier.objects.update_or_create(
                        organization=organization,
                        tax_id=tax_id,
                        defaults={
                            "legal_name": legal_name,
                            "trade_name": (row.get("trade_name") or "").strip(),
                            "country_code": (row.get("country_code") or "CO").strip(),
                        },
                    )
                    system = (row.get("external_system") or "").strip()
                    code = (row.get("external_code") or "").strip()
                    if system and code:
                        ExternalSupplierCode.objects.get_or_create(
                            supplier=supplier,
                            system=system,
                            company=(row.get("external_company") or "").strip(),
                            code=code,
                        )
                    count += 1
        except (UnicodeDecodeError, csv.Error, ValueError) as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f"Filas importadas: {count}.")
        return redirect("supplier_csv")

    return render(request, "integrations/supplier_csv.html")
