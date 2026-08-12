# Aceptación H5 — Primera publicación

## Completado localmente

- [x] Versión candidata definida.
- [x] Dockerfile y Compose con aplicación no privilegiada y PostgreSQL.
- [x] Configuración de secretos fuera del repositorio.
- [x] Scripts de instalación, verificación, copia y restauración.
- [x] Guías de administrador, proveedor y desarrollador.
- [x] Política de seguridad, contribución y licencias de terceros.
- [x] CI para pruebas deterministas y despliegue completo en contenedores.
- [x] Pruebas locales, comprobación endurecida, estáticos y smoke HTTP.
- [x] Revisión visual sin errores de consola.

## Cierre verificado

- [x] Ejecutar el despliegue Docker/PostgreSQL real y verificar salud.
- [x] Ejecutar copia y restauración sobre ese despliegue.
- [x] Crear repositorio público y ejecutar CI.
- [x] Corregir cualquier hallazgo del CI de contenedores.
- [x] Generar paquete desde un commit limpio y publicar release.

La ejecución de GitHub Actions desplegó los contenedores, verificó PostgreSQL,
eliminó un proveedor de prueba, restauró la copia y comprobó tanto el registro
recuperado como la salud HTTP final. Consulta `H5_REPORT.md` para las URLs y la
trazabilidad de la publicación.
