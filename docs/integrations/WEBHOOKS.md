# Webhooks

Supplier Hub utiliza una bandeja de salida persistente. Las transacciones de
negocio crean entregas pendientes y el comando `deliver_webhooks` las procesa.
Esto evita hacer depender una aprobación de la disponibilidad del ERP.

## Formato

El cuerpo sigue la forma esencial de CloudEvents 1.0:

```json
{
  "specversion": "1.0",
  "id": "uuid",
  "type": "qualification.approved",
  "source": "supplier-hub",
  "data": {}
}
```

Eventos iniciales:

- `supplier.created`
- `supplier.updated`
- `qualification.changes_requested`
- `qualification.approved`
- `qualification.conditional`
- `qualification.rejected`

## Verificación de firma

Cada solicitud lleva:

- `X-SupplierHub-Timestamp`
- `X-SupplierHub-Signature: v1=<hex>`

La firma es `HMAC-SHA256(secret, timestamp + "." + raw_body)`. El receptor debe
rechazar timestamps antiguos, calcular la firma sobre los bytes recibidos y
compararla en tiempo constante.

## Reintentos

Ejecuta periódicamente:

```powershell
.\.venv\Scripts\python.exe manage.py deliver_webhooks
```

Los fallos se reintentan con espera exponencial hasta ocho intentos. El
identificador del evento permite al receptor procesar de forma idempotente.

