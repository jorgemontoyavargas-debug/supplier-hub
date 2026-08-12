import uuid

from .models import WebhookDelivery, WebhookSubscription


def publish_event(*, organization, event_type, data):
    """Escribe en el outbox dentro de la transacción de negocio actual."""
    event_id = uuid.uuid4()
    subscriptions = WebhookSubscription.objects.filter(
        organization=organization, is_active=True
    )
    deliveries = []
    for subscription in subscriptions:
        if subscription.event_types and event_type not in subscription.event_types:
            continue
        deliveries.append(
            WebhookDelivery(
                subscription=subscription,
                event_id=event_id,
                event_type=event_type,
                payload={
                    "specversion": "1.0",
                    "id": str(event_id),
                    "type": event_type,
                    "source": "supplier-hub",
                    "data": data,
                },
            )
        )
    WebhookDelivery.objects.bulk_create(deliveries)
    return event_id
