# Adaptador ERPNext

El adaptador de referencia demuestra cómo consumir el contrato de Supplier Hub
sin convertir ERPNext en una dependencia. Solo utiliza la API REST estándar y
la biblioteca estándar de Python.

## Simulación

```powershell
.\.venv\Scripts\python.exe manage.py sync_erpnext_suppliers --organization pyme-demo
```

## Aplicación

Configura fuera del repositorio:

- `ERPNEXT_BASE_URL`
- `ERPNEXT_API_KEY`
- `ERPNEXT_API_SECRET`
- `ERPNEXT_COMPANY` opcional

Después ejecuta con `--apply`. El comando crea proveedores nuevos y actualiza
los que ya poseen un código externo `erpnext`. Las personalizaciones de ERPNext,
como campos propios de homologación, deben implementarse en un adaptador
derivado; el conector base no presupone que existan.

