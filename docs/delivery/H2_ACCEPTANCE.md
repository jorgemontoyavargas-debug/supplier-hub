# Aceptación H2 — Homologación funcional

## Recorrido

1. Un expediente enviado aparece en la bandeja de revisión.
2. Un revisor autorizado inicia la revisión.
3. Puede solicitar correcciones con fundamento.
4. Un aprobador registra aprobación, aprobación condicional o rechazo.
5. Aprobaciones exigen una vigencia futura.
6. El proveedor visualiza la decisión y puede reenviar después de correcciones.
7. Evidencias conservan versiones y fechas de expedición/vencimiento.
8. El proceso programado crea alertas dentro de los 30 días previos y marca
   expedientes vencidos.

## Permisos

- Revisor: iniciar revisión y solicitar correcciones.
- Aprobador/administrador: las mismas acciones y decisión final.
- Proveedor: editar únicamente borradores o expedientes con correcciones.
- Usuario relacionado: descargar evidencia; cualquier otro recibe denegación.

## Automatización

Ejecutar diariamente:

```powershell
.\.venv\Scripts\python.exe manage.py process_expirations
```

El comando es idempotente: no duplica alertas ni eventos de vencimiento.

