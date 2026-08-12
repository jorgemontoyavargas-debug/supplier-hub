# Informe H4 — 2026-08-12

## Resultado

Supplier Hub incorpora asistencia local opcional sin convertirla en autoridad de
negocio ni depender de una API comercial.

## Entregado

- Extracción real de PDF con texto embebido mediante pypdf.
- Adaptador opcional para Docling.
- Proveedor local reproducible por reglas.
- Proveedor Ollama con JSON Schema y validación literal de evidencia.
- Extracción de identificación fiscal y vencimiento.
- Propuestas con valor, evidencia, página, confianza, modelo y versión de prompt.
- Aceptación o rechazo humano; solo al aceptar se actualiza el dato.
- Detector de requisitos faltantes y documentos próximos a vencer.
- Plan de siguientes acciones sin ejecución autónoma.
- Resumen para proveedor y revisor.
- Conjunto de evaluación sintético y comando repetible.

## Verificación

- PDF sintético real procesado localmente: se extrajeron NIT y vencimiento con
  página de evidencia.
- Suite completa y evaluación sintética incluidas en `scripts/verify.ps1`.
- Prueba de aislamiento: un usuario ajeno no abre la asistencia.
- Prueba de aceptación: una propuesta confirmada actualiza la vigencia del
  documento y conserva su resolución.

## Límites conocidos

- El modo pypdf no realiza OCR.
- Docling todavía no forma parte del instalador básico.
- Ollama requiere instalación y modelo por parte del usuario.
- La calidad depende del tipo de documento; por eso las decisiones siguen siendo
  humanas y las métricas de aceptación/rechazo se conservarán.

