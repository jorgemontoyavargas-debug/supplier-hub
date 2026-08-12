# Informe H1 — 2026-08-12

## Resultado

El primer onboarding funcional está implementado. Un comprador puede crear un
proveedor y generar su invitación; el contacto puede activar una cuenta,
completar requisitos, adjuntar un PDF y enviar el expediente.

## Funciones entregadas

- Directorio y creación de proveedores.
- Contacto principal.
- Invitación aleatoria, expirable y de un solo uso.
- Token almacenado exclusivamente como hash SHA-256.
- Registro del usuario del proveedor.
- Portal inicial.
- Creación del expediente desde una plantilla activa.
- Respuestas y evidencias versionadas.
- Validación de requisitos antes del envío.
- Descarga autenticada de evidencia.
- Auditoría de creación, invitación, aceptación, inicio y envío.

## Límites que pasan a H2

- Interfaz propia para configurar plantillas y categorías.
- Bandeja de revisión, comentarios, correcciones y decisión.
- Fechas de expedición/vencimiento y recordatorios.
- Inspección profunda de tipo de archivo y antivirus, necesaria antes de una
  exposición pública no controlada.

