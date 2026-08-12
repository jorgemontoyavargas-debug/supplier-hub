import hashlib
import hmac
import json
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand
from django.utils import timezone

from integrations.models import WebhookDelivery


class Command(BaseCommand):
    help = "Entrega eventos pendientes con firma HMAC y reintentos exponenciales."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        now = timezone.now()
        deliveries = WebhookDelivery.objects.filter(
            status__in=(WebhookDelivery.Status.PENDING, WebhookDelivery.Status.FAILED),
            next_attempt_at__lte=now,
            attempts__lt=8,
            subscription__is_active=True,
        ).select_related("subscription")[: max(1, min(options["limit"], 200))]
        delivered_count = 0
        for delivery in deliveries:
            body = json.dumps(
                delivery.payload, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            timestamp = str(int(now.timestamp()))
            signature = hmac.new(
                delivery.subscription.secret.encode("utf-8"),
                timestamp.encode("ascii") + b"." + body,
                hashlib.sha256,
            ).hexdigest()
            request = Request(
                delivery.subscription.url,
                data=body,
                method="POST",
                headers={
                    "Content-Type": "application/cloudevents+json",
                    "User-Agent": "SupplierHub-Webhook/0.1",
                    "X-SupplierHub-Timestamp": timestamp,
                    "X-SupplierHub-Signature": f"v1={signature}",
                },
            )
            delivery.attempts += 1
            try:
                with urlopen(request, timeout=10) as response:
                    if not 200 <= response.status < 300:
                        raise HTTPError(
                            request.full_url,
                            response.status,
                            "Respuesta no exitosa",
                            response.headers,
                            None,
                        )
                delivery.status = WebhookDelivery.Status.DELIVERED
                delivery.delivered_at = timezone.now()
                delivery.last_error = ""
                delivered_count += 1
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                delivery.status = WebhookDelivery.Status.FAILED
                delivery.last_error = str(error)[:2000]
                delay_minutes = min(2 ** delivery.attempts, 24 * 60)
                delivery.next_attempt_at = timezone.now() + timedelta(
                    minutes=delay_minutes
                )
            delivery.save(
                update_fields=(
                    "attempts",
                    "status",
                    "delivered_at",
                    "last_error",
                    "next_attempt_at",
                    "updated_at",
                )
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Entregados: {delivered_count}. Procesados: {len(deliveries)}."
            )
        )
