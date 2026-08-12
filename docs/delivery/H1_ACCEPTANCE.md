# Aceptación H1 — Onboarding funcional

## Recorrido comprador

1. Un administrador inicia sesión.
2. Crea un proveedor y su contacto principal.
3. Genera una invitación con vigencia limitada.
4. El valor original del token se muestra una sola vez y no se persiste.

## Recorrido proveedor

1. Abre una invitación válida.
2. Crea contraseña y activa su cuenta.
3. La invitación queda consumida y no puede reutilizarse.
4. Inicia la plantilla de homologación configurada.
5. Responde requisitos y carga evidencia.
6. El sistema impide enviar mientras falten requisitos obligatorios.
7. Envía el expediente y este queda en estado `enviado`.

## Seguridad verificable

- Un usuario no ve proveedores de organizaciones ajenas.
- Un observador no puede crear proveedores ni invitarlos.
- Un usuario no relacionado no descarga evidencia privada.
- Los archivos tienen límite de tamaño y extensiones permitidas.
- Acciones principales generan eventos de auditoría.

## Evidencia

La suite automatizada cubre creación, aislamiento, invitación de un solo uso,
expiración, permisos, envío obligatorio y descarga privada. El informe de cierre
se encuentra en `H1_REPORT.md`.

