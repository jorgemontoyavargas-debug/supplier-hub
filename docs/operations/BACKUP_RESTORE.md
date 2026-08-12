# Copias y restauración

## Copia

Con el despliegue activo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\backup.ps1
```

Se crean un dump PostgreSQL, un archivo de medios y sus hashes dentro de
`backups/<fecha>`. Copia ese directorio a almacenamiento separado y protegido.

En Linux o macOS:

```text
./scripts/backup.sh
```

## Restauración

La restauración reemplaza los datos actuales y debe realizarse durante una
ventana de mantenimiento:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restore.ps1 `
  -BackupDirectory .\backups\YYYYMMDD-HHMMSS -ConfirmRestore
```

El script solo acepta copias ubicadas dentro del directorio `backups` del
proyecto y exige confirmación explícita. Después ejecuta
`scripts/verify-deployment.ps1` y prueba la descarga de una evidencia.

Una copia no se considera válida hasta haber sido restaurada en un entorno de
prueba. El procedimiento de release incluye esa comprobación.

En Linux o macOS:

```text
CONFIRM_RESTORE=yes ./scripts/restore.sh ./backups/YYYYMMDD-HHMMSS
```
