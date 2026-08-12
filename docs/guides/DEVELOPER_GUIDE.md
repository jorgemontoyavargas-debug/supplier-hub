# Guía del desarrollador

## Entorno

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

## Módulos

- `accounts`: identidad.
- `organizations`: organización y roles.
- `suppliers`: maestro, contactos e invitaciones.
- `qualifications`: requisitos, evidencias y decisiones.
- `integrations`: CSV, API, outbox y adaptadores.
- `intelligence`: extracción, proveedores locales y propuestas.
- `core`: auditoría, notificaciones y páginas comunes.

## Reglas

- Filtra toda consulta por organización o relación explícita con el proveedor.
- Añade una prueba negativa de autorización por cada recurso nuevo.
- No actualices estados mediante CRUD genérico; usa transiciones de dominio.
- No hagas llamadas externas dentro de una decisión de negocio; escribe en el
  outbox.
- La IA produce `AISuggestion`; nunca escribe directamente sin resolución.
- Crea una migración para cada cambio persistente.
- Registra decisiones estructurales en un ADR.

## API y eventos

El contrato está en `docs/api/openapi.yaml`. Los consumidores deben usar una
clave idempotente por operación y almacenar los UUID de eventos procesados.

