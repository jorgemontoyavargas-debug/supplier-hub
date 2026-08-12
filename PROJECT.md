# Gobierno del proyecto

## Objetivo

Construir una aplicación útil y gratuita que permita a una pyme invitar,
registrar, documentar, revisar, homologar y mantener proveedores sin requerir
un ERP ni una suscripción externa.

## Decisiones confirmadas

| Decisión | Valor |
| --- | --- |
| Nombre provisional | Supplier Hub |
| Licencia | AGPL-3.0-only |
| Desarrollo inicial | Local |
| Publicación | Al alcanzar el primer hito funcional y verificable |
| Idioma inicial | Español |
| Internacionalización | Preparada desde la primera versión |
| Servicios de pago obligatorios | Ninguno |
| IA | Opcional, local o intercambiable, nunca requisito del núcleo |
| Documentos de prueba iniciales | Sintéticos; reales cuando estén disponibles |

## Responsabilidad

Codex asume producto, arquitectura, implementación, pruebas, seguridad,
documentación y empaquetado. Las consultas al propietario se reservan para
decisiones legales, comerciales, irreversibles o que cambien materialmente el
alcance.

## Hitos

### H0 — Base ejecutable

- [x] Alcance, arquitectura y modelo de dominio aprobados por criterios objetivos.
- [x] Repositorio local organizado.
- [x] Entorno reproducible y controles automáticos de calidad.
- [x] Aplicación arranca y expone una comprobación de salud.

Estado: completado el 2026-08-12. Evidencia en
`docs/delivery/H0_REPORT.md`.

### H1 — Onboarding funcional

- [x] Organización, usuarios, roles, proveedores, contactos y categorías.
- [x] Invitación y portal del proveedor.
- [x] Creación y envío de un expediente.
- [x] Datos demostrativos y pruebas del recorrido principal.

Estado: completado el 2026-08-12. Evidencia en
`docs/delivery/H1_REPORT.md`.

### H2 — Homologación funcional

- [x] Plantillas, requisitos, cuestionarios y documentos versionados.
- [x] Revisión, correcciones, decisión y trazabilidad.
- [x] Vencimientos y notificaciones internas.

Estado: completado el 2026-08-12. Evidencia en
`docs/delivery/H2_REPORT.md`.

### H3 — Integración abierta

- Importación y exportación CSV.
- API documentada y webhooks firmados.
- Identificadores externos, idempotencia y bitácora de sincronización.
- Conector de referencia para ERPNext si no compromete el núcleo.

### H4 — Asistencia con IA

- Procesamiento documental local opcional.
- Extracción estructurada con evidencia.
- Prellenado sujeto a confirmación.
- Detector de faltantes y resumen para el revisor.
- Evaluaciones repetibles sobre documentos sintéticos y anonimizados.

### H5 — Primera publicación

- Instalación documentada.
- Copias de seguridad y restauración probadas.
- Pruebas de permisos y recorrido end-to-end.
- Guías de administrador, proveedor y desarrollador.
- Release reproducible preparado para publicación.

## Definición global de terminado

Un hito se considera terminado únicamente cuando su recorrido de aceptación es
repetible, cuenta con pruebas proporcionadas al riesgo y está documentado. Una
pantalla sin persistencia, permisos o validación no constituye una función
terminada.
