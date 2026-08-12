import json
from urllib.parse import quote
from urllib.request import Request, urlopen


def supplier_to_erpnext(supplier):
    """Mapeo conservador a campos estándar del DocType Supplier de ERPNext."""
    return {
        "supplier_name": supplier.legal_name,
        "supplier_type": "Company",
        "tax_id": supplier.tax_id,
        "country": supplier.country_code,
    }


class ERPNextClient:
    def __init__(self, *, base_url, api_key, api_secret, timeout=15):
        self.base_url = base_url.rstrip("/")
        self.authorization = f"token {api_key}:{api_secret}"
        self.timeout = timeout

    def upsert_supplier(self, *, payload, remote_name=None):
        if remote_name:
            path = f"/api/resource/Supplier/{quote(remote_name, safe='')}"
            method = "PUT"
        else:
            path = "/api/resource/Supplier"
            method = "POST"
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={
                "Authorization": self.authorization,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SupplierHub-ERPNext/0.1",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))["data"]
