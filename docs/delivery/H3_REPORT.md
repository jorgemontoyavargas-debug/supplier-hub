# Informe H3 — 2026-08-12

## Resultado

Supplier Hub puede operar sin ERP y también ofrece una frontera de integración
abierta. Ninguna función requiere un servicio comercial.

## Entregado

- Importación y exportación CSV UTF-8 desde la interfaz.
- API REST `v1` documentada con OpenAPI 3.1.
- Credenciales aleatorias almacenadas como hash y mostradas una sola vez.
- Aislamiento de API por organización.
- Upsert de proveedores por identificación fiscal o código externo.
- Clave idempotente obligatoria y detección de reutilización conflictiva.
- Webhooks en bandeja persistente, firmados con HMAC y con reintentos.
- Registros consultables de solicitudes idempotentes y entregas.
- Adaptador ERPNext con simulación predeterminada y aplicación explícita.

## Verificación

- 27 pruebas automatizadas correctas.
- API autenticada, idempotencia y aislamiento cubiertos.
- Importación seguida de exportación CSV cubierta.
- Firma y entrega única de webhook simuladas sin tráfico externo.
- Mapeo conservador a campos estándar de ERPNext probado.

## Uso

- Contrato: `docs/api/openapi.yaml`.
- Webhooks: `docs/integrations/WEBHOOKS.md`.
- ERPNext: `docs/integrations/ERPNEXT.md`.

