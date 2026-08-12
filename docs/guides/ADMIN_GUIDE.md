# Guía del administrador

## Preparación inicial

1. Ingresa a `/admin/` con el superusuario.
2. Crea la organización compradora.
3. Asocia usuarios mediante membresías y roles.
4. Crea categorías.
5. Crea una plantilla de homologación y sus requisitos.

Los requisitos admiten texto, número, fecha, sí/no, selección y documento. Usa
una nueva versión de plantilla cuando cambie materialmente el cuestionario.

## Invitar proveedor

1. Abre **Proveedores → Nuevo proveedor**.
2. Registra identificación y contacto principal.
3. En el detalle, genera la invitación.
4. Copia el enlace en ese momento: el token original no se almacena.

## Revisar

1. Abre **Revisiones**.
2. Inicia la revisión del expediente enviado.
3. Registra comentarios por respuesta cuando corresponda.
4. Solicita correcciones o, si tienes rol aprobador, decide.
5. Toda aprobación necesita una fecha de vigencia futura.

## Integrar

Usa CSV para una integración manual. Para API, crea una credencial con
`create_api_key` y conserva el valor en un gestor de secretos. Los webhooks se
configuran en la administración y se entregan mediante el comando programado.

