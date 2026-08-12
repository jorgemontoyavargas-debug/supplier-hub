# Aceptación H0 — Base ejecutable

## Recorrido

1. Crear entorno con `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1`.
2. Aplicar migraciones sin intervención.
3. Cargar datos demo dos veces sin duplicarlos.
4. Arrancar la aplicación.
5. Consultar `/salud/` y recibir estado de aplicación y base de datos.
6. Iniciar sesión y visualizar solamente las organizaciones asignadas.
7. Ejecutar `powershell -ExecutionPolicy Bypass -File scripts/verify.ps1` sin errores.

## Evidencia requerida

- `manage.py check` sin errores.
- No existen migraciones pendientes.
- Pruebas automatizadas verdes.
- `check --deploy --fail-level WARNING` limpio con el perfil endurecido de
  verificación. HSTS preload permanece desactivado por defecto porque activarlo
  para un dominio real es una decisión operativa de largo alcance.
- Smoke test HTTP real del inicio y healthcheck.

## Fuera de H0

H0 demuestra la plataforma técnica, no el onboarding completo. H1 exige crear e
invitar proveedores desde una interfaz propia y completar el primer expediente.
