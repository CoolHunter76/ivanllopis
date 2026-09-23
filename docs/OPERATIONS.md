# Guia operativa

## Mapa de entornos

| Entorno | Rama | URL publica | Puerto local | Directorio servidor |
| --- | --- | --- | --- | --- |
| Staging | `develop` | `https://staging.ivanllopis.net` | `8001` | `/opt/ivanllopis/staging` |
| Produccion | `master` | `https://ivanllopis.net` | `8000` | `/opt/ivanllopis/app` |

Los despliegues deben mantener repositorios, contenedores, proyectos Compose, puertos y rutas Nginx independientes.

## Componentes operativos versionados

- `server/deploy-ivanllopis-staging`: despliegue de staging.
- `server/deploy-ivanllopis`: despliegue de produccion.
- `server/verify-ivanllopis-isolation`: verificacion de aislamiento.
- `scripts/public_smoke.py`: comprobacion publica de salud, feeds, cache y seguridad.
- `scripts/check-security-headers.sh`: comprobacion focalizada de cabeceras.

Las copias instaladas en `/usr/local/sbin` deben mantenerse sincronizadas con las versiones del repositorio.

## Verificacion habitual

```powershell
ruff check .
ruff format --check .
pytest
python scripts/public_smoke.py --output public-smoke-report.json
```

El informe `public-smoke-report.json` es diagnostico temporal y no debe confirmarse en Git.

## Diagnostico de despliegue

1. Consulta `/health` y verifica `status`, `deployment.environment`, `deployment.version` y `deployment.commit`.
2. Confirma que el commit publicado coincide con el HEAD de la rama desplegada.
3. Revisa el workflow de CD correspondiente.
4. Revisa los logs del servicio web mediante Docker Compose en el servidor.
5. Ejecuta la verificacion de aislamiento si hay dudas sobre puertos, contenedores o rutas Nginx.
6. Ejecuta Uptime Monitor y descarga `public-smoke-report` si falla una comprobacion publica.

## Recuperacion

La recuperacion consiste en volver a desplegar un commit conocido de la rama autorizada. No se deben editar archivos de aplicacion dentro del contenedor.

- Staging solo admite `develop`.
- Produccion solo admite `master`.
- La identidad devuelta por `/health` debe coincidir exactamente con el despliegue esperado.
- Si la comprobacion de salud no converge, conserva los logs antes de reconstruir o reiniciar.

## Monitorizacion

Uptime Monitor se ejecuta manualmente y mediante programacion. Valida:

- Salud e identidad de produccion y staging.
- SHA completo de Git.
- Feeds JSON y Atom.
- Peticiones HEAD.
- ETag, Last-Modified, Content-Length y Cache-Control.
- Respuestas condicionales 304.
- Cabeceras HTTP globales de seguridad.


### Sincronizacion de scripts operativos

La instalacion inicial requiere una unica operacion administrativa para copiar `server/sync-ivanllopis-operational-scripts` a `/usr/local/sbin` e instalar `server/ivanllopis-script-sync.sudoers` mediante `visudo`. A partir de ese momento, CD Staging y CD Production sincronizan las copias autorizadas antes de desplegar.

Comprobacion manual, sin modificar archivos:

```text
sudo /usr/local/sbin/sync-ivanllopis-operational-scripts staging
sudo /usr/local/sbin/sync-ivanllopis-operational-scripts production
```

No se aceptan rutas libres ni el objetivo `all`. Cada entorno usa una ruta de repositorio fija y una lista cerrada de ejecutables.
