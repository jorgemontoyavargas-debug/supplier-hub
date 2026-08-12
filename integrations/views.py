import hashlib
import json
from functools import wraps

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from suppliers.models import ExternalSupplierCode, Supplier

from .models import APICredential, IdempotencyRecord
from .services import publish_event


def api_authentication(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, raw_key = authorization.partition(" ")
        if scheme.lower() != "bearer" or not raw_key:
            return JsonResponse({"error": "unauthorized"}, status=401)
        credential = APICredential.authenticate(raw_key)
        if credential is None:
            return JsonResponse({"error": "unauthorized"}, status=401)
        request.api_credential = credential
        return view(request, *args, **kwargs)

    return wrapped


def _supplier_payload(supplier):
    return {
        "id": str(supplier.id),
        "legal_name": supplier.legal_name,
        "trade_name": supplier.trade_name,
        "tax_id": supplier.tax_id,
        "country_code": supplier.country_code,
        "status": supplier.status,
        "external_codes": [
            {"system": item.system, "company": item.company, "code": item.code}
            for item in supplier.external_codes.all()
        ],
        "updated_at": supplier.updated_at.isoformat(),
    }


@csrf_exempt
@api_authentication
def suppliers_api(request):
    organization = request.api_credential.organization
    if request.method == "GET":
        try:
            limit = min(max(int(request.GET.get("limit", 50)), 1), 100)
        except ValueError:
            return JsonResponse({"error": "invalid_limit"}, status=400)
        suppliers = (
            Supplier.objects.filter(organization=organization)
            .prefetch_related("external_codes")
            .order_by("legal_name")[:limit]
        )
        return JsonResponse({"data": [_supplier_payload(item) for item in suppliers]})
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    idempotency_key = request.headers.get("Idempotency-Key", "").strip()
    if not idempotency_key:
        return JsonResponse({"error": "idempotency_key_required"}, status=400)
    if len(idempotency_key) > 150:
        return JsonResponse({"error": "idempotency_key_too_long"}, status=400)
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)
    request_hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    existing = IdempotencyRecord.objects.filter(
        organization=organization, key=idempotency_key, endpoint="POST /api/v1/suppliers"
    ).first()
    if existing:
        if existing.request_hash != request_hash:
            return JsonResponse({"error": "idempotency_conflict"}, status=409)
        return JsonResponse(existing.response_body, status=existing.status_code)

    required = [field for field in ("legal_name", "tax_id") if not body.get(field)]
    if required:
        return JsonResponse({"error": "missing_fields", "fields": required}, status=400)

    with transaction.atomic():
        external = body.get("external_code") or {}
        supplier = None
        if external.get("system") and external.get("code"):
            external_match = ExternalSupplierCode.objects.filter(
                supplier__organization=organization,
                system=external["system"],
                company=external.get("company", ""),
                code=external["code"],
            ).select_related("supplier").first()
            supplier = external_match.supplier if external_match else None
        supplier = supplier or Supplier.objects.filter(
            organization=organization, tax_id=body["tax_id"]
        ).first()
        created = supplier is None
        if created:
            supplier = Supplier(organization=organization, tax_id=body["tax_id"])
        supplier.legal_name = body["legal_name"]
        supplier.trade_name = body.get("trade_name", "")
        supplier.country_code = body.get("country_code", "CO")
        supplier.save()
        if external.get("system") and external.get("code"):
            ExternalSupplierCode.objects.get_or_create(
                supplier=supplier,
                system=external["system"],
                company=external.get("company", ""),
                code=external["code"],
            )
        supplier = Supplier.objects.prefetch_related("external_codes").get(id=supplier.id)
        response_body = {"data": _supplier_payload(supplier), "created": created}
        status_code = 201 if created else 200
        IdempotencyRecord.objects.create(
            organization=organization,
            key=idempotency_key,
            endpoint="POST /api/v1/suppliers",
            request_hash=request_hash,
            status_code=status_code,
            response_body=response_body,
        )
        publish_event(
            organization=organization,
            event_type="supplier.created" if created else "supplier.updated",
            data=response_body["data"],
        )
    return JsonResponse(response_body, status=status_code)

# Create your views here.
