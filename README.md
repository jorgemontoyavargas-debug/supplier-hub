# Supplier Hub

Supplier Hub es una plataforma abierta de onboarding y homologación de
proveedores para pymes. Funciona de forma independiente, puede integrarse con
un ERP y admite capacidades opcionales de inteligencia artificial local.

## Estado

Versión candidata `0.1.0-rc.1`. El producto cubre onboarding, expediente,
revisión, homologación, vigencias, integración abierta y asistencia local. El
nombre es provisional.

## Principios

- La funcionalidad esencial no depende de servicios de pago.
- Instalación self-hosted y reproducible.
- Español como idioma inicial e internacionalización desde el diseño.
- Integración mediante CSV, API REST y webhooks.
- IA opcional, auditable y con aprobación humana.
- Ningún modelo de IA puede aprobar o rechazar por sí solo a un proveedor.

## Inicio rápido para desarrollo

Requiere Python 3.12 o posterior.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Después abre `http://127.0.0.1:8000`. Los datos de demostración crean:

- Usuario: `admin.demo`
- Contraseña inicial: `supplierhub-demo`

Estas credenciales son exclusivamente locales y deben cambiarse en cualquier
entorno compartido.

Para verificar el proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Si Python no está disponible como `python` o `py`, pasa su ruta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -PythonExecutable "C:\ruta\python.exe"
```

## Licencia

Supplier Hub se distribuye bajo GNU Affero General Public License v3.0
(AGPL-3.0-only). Consulta [LICENSE](LICENSE).

Consulta [PROJECT.md](PROJECT.md) para el alcance y los hitos activos.

## Documentación

- [Instalación](docs/operations/INSTALLATION.md)
- [Administrador](docs/guides/ADMIN_GUIDE.md)
- [Proveedor](docs/guides/SUPPLIER_GUIDE.md)
- [Desarrollador](docs/guides/DEVELOPER_GUIDE.md)
- [API OpenAPI](docs/api/openapi.yaml)
- [IA local](docs/ai/LOCAL_AI.md)
- [Copias y restauración](docs/operations/BACKUP_RESTORE.md)
