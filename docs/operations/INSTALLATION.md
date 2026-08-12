# Instalación

## Evaluación local en Windows

Requiere Python 3.12+:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Este perfil usa SQLite y datos sintéticos. No debe exponerse directamente a
Internet.

## Instalación self-hosted con contenedores

Requiere Docker Engine con Compose o una implementación compatible.

1. Copia `.env.docker.example` como `.env`.
2. Genera dos secretos independientes y reemplaza los valores de ejemplo.
3. Ajusta hosts y zona horaria.
4. Ejecuta `docker compose up -d --build`.
5. Crea el administrador:

```text
docker compose exec web python manage.py createsuperuser
```

La aplicación queda en `http://localhost:8000`. Este modo usa
`SUPPLIER_HUB_HTTPS=false` exclusivamente para evaluación local. Para acceso
remoto debe situarse detrás de un proxy HTTPS y configurarse:

```text
SUPPLIER_HUB_HTTPS=true
SUPPLIER_HUB_ALLOWED_HOSTS=proveedores.ejemplo.com
SUPPLIER_HUB_CSRF_TRUSTED_ORIGINS=https://proveedores.ejemplo.com
```

No habilites HSTS preload hasta confirmar que todo el dominio y sus subdominios
se servirán permanentemente por HTTPS.

## Procesos programados

Ejecuta mediante cron o el programador del sistema:

```text
docker compose exec -T web python manage.py process_expirations
docker compose exec -T web python manage.py deliver_webhooks
```

Ambos comandos son idempotentes.

## Linux sin contenedores

Para evaluación local:

```text
./scripts/setup.sh
.venv/bin/python manage.py runserver
```

La ejecución de producción sin contenedores requiere PostgreSQL, Gunicorn, un
usuario de sistema y un proxy HTTPS; el contenedor es el método soportado para la
primera candidata.

## IA local

El perfil básico de reglas y PDF está incluido. Ollama se instala por separado y
se activa mediante variables documentadas en `docs/ai/LOCAL_AI.md`. No es
necesario para usar Supplier Hub.
