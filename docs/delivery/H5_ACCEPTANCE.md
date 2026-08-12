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

## Pendiente para cerrar H5

- [ ] Ejecutar el despliegue Docker/PostgreSQL real y verificar salud.
- [ ] Ejecutar copia y restauración sobre ese despliegue.
- [ ] Crear repositorio público y ejecutar CI.
- [ ] Corregir cualquier hallazgo del CI de contenedores.
- [ ] Generar paquete desde un commit limpio y publicar release.

El equipo actual no tiene Docker ni WSL. GitHub CLI está instalado, pero no hay
sesión autenticada. Estos puntos no se declararán completados hasta contar con
evidencia externa real.

