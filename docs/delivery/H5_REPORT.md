# Informe H5 — Primera publicación

## Resultado

Supplier Hub `0.1.0-rc.1` quedó publicado como software open source bajo
AGPL-3.0-only. El código fuente, la automatización de pruebas y el paquete de
instalación son accesibles sin suscripciones obligatorias.

## Evidencia verificable

| Criterio | Evidencia |
| --- | --- |
| Repositorio público | https://github.com/jorgemontoyavargas-debug/supplier-hub |
| CI Docker/PostgreSQL aprobada | https://github.com/jorgemontoyavargas-debug/supplier-hub/actions/runs/31625881222 |
| Pruebas deterministas | 32 pruebas Django y evaluación local de IA 3/3 |
| Despliegue real | Compose construyó y levantó aplicación y PostgreSQL saludables |
| Copia y restauración | La CI eliminó el proveedor demo, restauró el dump y comprobó su recuperación |
| Salud posterior | `/salud/` confirmó aplicación y base de datos después de restaurar |
| Prerelease | https://github.com/jorgemontoyavargas-debug/supplier-hub/releases/tag/v0.1.0-rc.1 |

## Hallazgo corregido

La primera ejecución externa detectó que la comprobación final podía ocurrir
antes de que Gunicorn volviera a escuchar tras una restauración. El script fue
corregido para esperar la salud HTTP y de base de datos, con reintentos y logs
diagnósticos. La ejecución posterior pasó completa.

## Contenido del hito

- Instalación local y en contenedores documentada.
- PostgreSQL como base de producción y SQLite para evaluación local.
- Copia y restauración de base de datos y documentos.
- Guías para administrador, proveedor y desarrollador.
- Licencia, seguridad, contribución y avisos de terceros.
- Paquete reproducible generado con `git archive` desde un commit limpio.

## Alcance posterior

Esta prerelease demuestra el primer producto funcional. Marca, traducciones
adicionales, conectores ERP específicos y modelos de IA adicionales pertenecen
a hitos futuros y no son requisitos para instalar o usar el núcleo actual.
