# ADR-0001 — Fundación tecnológica

- Estado: reemplazada por ADR-0002
- Fecha: 2026-08-12

## Contexto

El producto debe ser gratuito, self-hosted, modificable y construible por un
equipo extremadamente pequeño. Necesita permisos, workflows, portal, archivos,
tareas programadas, API e internacionalización.

## Decisión

Usar una aplicación independiente sobre Frappe Framework, con ERPNext como
integración opcional y no como dependencia. Empezar como monolito modular y
distribuir mediante Docker Compose.

## Consecuencias

- Se acelera el núcleo funcional y se conserva una API estándar.
- La experiencia del portal requerirá personalización específica.
- El despliegue tiene más componentes que una aplicación SQLite simple.
- Docker no está instalado actualmente en el equipo de desarrollo; no bloquea
  la definición ni el código, pero la aceptación de H0 exige verificar el
  despliegue en un runtime compatible.

## Criterio de revisión

Reconsiderar solamente si el prototipo H0 no puede instalarse de manera
reproducible, el portal exige un fork del framework o los permisos no permiten
aislar correctamente a los proveedores.

## Resultado de la revisión

El entorno de desarrollo no dispone de Docker y Frappe exige una topología de
servicios y herramientas significativamente mayor que la necesaria para el
producto. Esa carga contradice la experiencia de instalación sencilla buscada
para una pyme. La decisión fue reemplazada antes de implementar dominio.

