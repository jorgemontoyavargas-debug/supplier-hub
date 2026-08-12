# PRD — Supplier Hub

## Problema

Las pymes gestionan el alta y la homologación de proveedores mediante correo,
carpetas y hojas de cálculo. Esto dificulta conocer qué falta, quién aprobó,
qué documento venció y si el proveedor continúa habilitado.

## Usuarios

- Administrador de la empresa compradora.
- Responsable de compras o categoría.
- Revisor de calidad, cumplimiento o finanzas.
- Aprobador.
- Administrador y colaborador del proveedor.
- Auditor u observador.

## Propuesta de valor

Una pyme puede instalar Supplier Hub, configurar sus requisitos, invitar un
proveedor y completar una homologación trazable sin contratar otro servicio.

## Recorrido crítico

1. El administrador configura organización, categorías y requisitos.
2. Invita al proveedor mediante un enlace de uso limitado.
3. El proveedor registra empresa y contactos.
4. Responde el cuestionario y adjunta los documentos exigidos.
5. Envía el expediente.
6. El revisor acepta evidencias o solicita correcciones.
7. Un aprobador decide: aprobado, condicional o rechazado.
8. El sistema registra la decisión y controla los vencimientos.

## Estados del expediente

`borrador`, `enviado`, `en_revision`, `correcciones_solicitadas`,
`aprobado`, `condicional`, `rechazado`, `suspendido`, `vencido`.

Toda transición se valida en servidor, exige permisos y genera un evento de
auditoría inmutable desde la interfaz ordinaria.

## Alcance de la primera publicación

### Incluido

- Instalación para una organización compradora por instancia.
- Usuarios y permisos por rol.
- Maestro de proveedores y contactos.
- Árbol de categorías.
- Plantillas de homologación configurables.
- Preguntas de texto, número, fecha, selección, sí/no y archivo.
- Requisitos documentales por categoría.
- Versiones de documentos y fechas de vigencia.
- Revisión, comentarios, correcciones y decisión.
- Tareas y alertas internas.
- Historial auditable.
- Panel operativo básico.
- CSV, API REST y webhooks.
- Datos de demostración.

### No incluido

- Contabilidad, pagos, impuestos o facturación electrónica.
- Licitaciones, subastas o contratos avanzados.
- Firma electrónica.
- Fuentes comerciales de riesgo.
- Aprobación autónoma mediante IA.
- Infraestructura de alta disponibilidad.

## Requisitos no funcionales

- Ninguna dependencia esencial requiere suscripción.
- Secretos fuera del repositorio.
- Contraseñas con algoritmos de hash mantenidos por el framework elegido.
- Protección contra acceso entre proveedores.
- Archivos privados y autorizados antes de su descarga.
- Registro de acciones sensibles.
- Copia y restauración documentadas.
- Interfaz usable en móvil para el proveedor.
- Accesibilidad básica WCAG 2.2 AA en los recorridos principales.
- Exportación de datos para evitar dependencia tecnológica.

## IA

La aplicación funciona completamente con IA desactivada. Cuando se activa, la
IA genera propuestas, nunca hechos definitivos. Cada propuesta conserva valor,
confianza, fuente, ubicación en el documento, modelo, versión y resolución
humana.

## Métricas de producto

- Tiempo desde invitación hasta envío.
- Porcentaje de expedientes completos al primer envío.
- Tiempo de revisión.
- Número de correcciones por expediente.
- Documentos vencidos o próximos a vencer.
- Porcentaje de propuestas de IA aceptadas, corregidas y rechazadas.

