# Informe H0 — 2026-08-12

## Resultado

La base ejecutable está aceptada. Supplier Hub arranca como aplicación Django,
persiste datos, autentica usuarios, aísla la vista inicial por membresías,
expone salud operativa y contiene el primer modelo de proveedores y
homologaciones.

## Evidencia

- `manage.py check`: sin problemas.
- `makemigrations --check --dry-run`: sin cambios pendientes.
- 10 pruebas automatizadas: correctas.
- `check --deploy --fail-level WARNING`: correcto con perfil endurecido.
- Smoke HTTP:
  - `/salud/`: HTTP 200, aplicación y base de datos `ok`.
  - `/`: HTTP 200 y contenido principal en español.
- `seed_demo` ejecutado dos veces sin duplicar usuario u organización.

## Decisiones

- Frappe fue reemplazado por Django 5.2 LTS mediante ADR-0002.
- SQLite se usa para evaluación; PostgreSQL será el perfil de producción.
- El frontend inicial se renderiza en servidor y no requiere Node ni CDN.

## Limitaciones conocidas

- La administración Django permite explorar el dominio, pero todavía no es el
  portal de onboarding de H1.
- No existe todavía invitación con token ni acceso acotado para el proveedor.
- Los archivos aún no se descargan mediante una vista privada autorizada.
- Docker y el perfil PostgreSQL siguen pendientes para el empaquetado.

## Próximo hito

H1 implementará la experiencia propia para crear un proveedor, emitir una
invitación de uso único, registrar al contacto y preparar/enviar un expediente.

