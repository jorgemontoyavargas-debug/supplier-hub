# Arquitectura inicial

## Vista general

Supplier Hub es un monolito modular Django. El núcleo no depende de ERP ni de
IA. El procesamiento documental se añadirá como trabajador opcional detrás de
un contrato interno.

```text
Navegador
   │ HTTPS
   ▼
Django ─── identidad y organizaciones
   ├────── proveedores y categorías
   ├────── homologaciones y documentos
   ├────── auditoría y notificaciones
   ├────── API, CSV y webhooks
   └────── puerto de IA (opcional) ── Docling/OCR ── modelo local
   │
   ▼
SQLite (evaluación) / PostgreSQL (producción)
```

## Módulos actuales

- `accounts`: usuario extensible e idioma preferido.
- `organizations`: empresa compradora y membresías con rol.
- `suppliers`: proveedor, contactos, categorías y códigos ERP.
- `qualifications`: plantillas, requisitos, expedientes, respuestas y archivos.
- `core`: páginas comunes y auditoría.

## Invariantes

- Toda entidad de negocio pertenece directa o indirectamente a una organización.
- Una consulta presentada a un usuario se filtra por sus membresías activas.
- Las transiciones de expedientes se validan en el servidor.
- Una organización no puede enlazar proveedores o plantillas de otra.
- Los eventos de auditoría no se editan desde la administración ordinaria.
- Un proveedor puede conservar varios códigos por ERP y sociedad.
- La IA solo crea propuestas con evidencia; no modifica datos aprobados.

## Despliegue

- Evaluación: entorno virtual, SQLite y servidor Django.
- Producción básica: contenedor de aplicación, PostgreSQL y proxy TLS.
- IA local: perfil adicional, nunca dependencia del perfil básico.

El proyecto no requiere Node.js para funcionar. Los estilos y comportamientos
esenciales no dependerán de una CDN.

## Evolución controlada

Se incorporará una cola únicamente cuando OCR, correo o webhooks necesiten
reintentos en segundo plano. Se incorporará almacenamiento S3 compatible cuando
el sistema de archivos local sea insuficiente. Ambas capacidades usarán
adaptadores y mantendrán alternativas gratuitas y autoalojables.

