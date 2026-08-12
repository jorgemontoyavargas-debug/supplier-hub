# Modelo de amenazas inicial

## Activos

- Identidad fiscal, contactos y documentos del proveedor.
- Decisiones y comentarios de homologación.
- Credenciales, enlaces de invitación y secretos de integración.
- Registro de auditoría.

## Amenazas prioritarias y controles

| Amenaza | Control inicial |
| --- | --- |
| Acceso de un proveedor a otro | Consultas acotadas por organización/proveedor y pruebas negativas |
| Referencias cruzadas manipuladas | Validaciones de dominio y filtros del servidor |
| Descarga directa de documentos | Archivos privados servidos tras autorización |
| Invitaciones reutilizadas | Token aleatorio, vencimiento y consumo único |
| Carga maliciosa | Tamaño y tipo permitidos, nombre seguro, almacenamiento no ejecutable |
| CSRF o secuestro de sesión | Middleware Django, cookies seguras en producción y rotación de sesión |
| Fuerza bruta | Límites de intentos antes de exposición pública |
| Webhook falsificado | Firma HMAC, timestamp, idempotencia y reintentos |
| Prompt injection documental | Texto tratado como dato; herramientas y acciones con lista permitida |
| Filtración a un LLM externo | IA desactivada por defecto y consentimiento/configuración explícitos |
| Alteración de auditoría | Sin edición ordinaria; exportación y retención definidas |

## Pendientes antes de publicación

- Prueba automatizada de autorización sobre cada recurso privado.
- Encabezados de seguridad y configuración TLS del proxy.
- Política de retención y borrado.
- Análisis de dependencias y secretos en CI.
- Procedimiento de reporte responsable de vulnerabilidades.

