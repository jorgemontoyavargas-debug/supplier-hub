# ADR-0002 — Monolito modular con Django

- Estado: aceptada
- Fecha: 2026-08-12

## Contexto

Supplier Hub necesita autenticación, permisos, administración, formularios,
migraciones, archivos, internacionalización y tareas recurrentes. La instalación
debe ser razonable para una pyme y el desarrollo debe poder verificarse sin una
infraestructura distribuida.

## Decisión

Utilizar Django 5.2 LTS y Python 3.12 como núcleo. Durante desarrollo y pequeñas
instalaciones se admite SQLite; el perfil de producción soportará PostgreSQL.
La interfaz inicial empleará HTML renderizado en servidor y JavaScript
progresivo, evitando una segunda aplicación frontend hasta que exista una
necesidad demostrada.

## Motivos

- Django incluye usuarios, permisos, protección CSRF, ORM, migraciones, i18n,
  administración y framework de pruebas.
- Un proceso web y una base SQLite permiten una evaluación local ligera.
- PostgreSQL ofrece un camino de crecimiento sin cambiar el modelo de dominio.
- Python permite integrar posteriormente Docling, OCR y modelos locales.
- Menos dependencias reducen superficie de ataque y mantenimiento.

## Consecuencias

- Algunos workflows y el portal deben implementarse en el producto.
- La API y OpenAPI se añadirán como módulo explícito en H3.
- Las tareas programadas comenzarán como comandos idempotentes; una cola se
  introducirá solo cuando haya trabajo que no pueda resolverse de ese modo.
- ERPNext será un sistema externo conectado mediante el contrato canónico.

## Alternativas descartadas

- Frappe: excelente base empresarial, pero demasiado pesada para el instalador
  inicial y difícil de verificar en el entorno disponible sin Docker.
- SPA separada: mayor complejidad de autenticación, despliegue y accesibilidad
  sin aportar valor al primer recorrido.
- Microservicios: fronteras operativas prematuras para un equipo de desarrollo
  y una instalación pequeña.

