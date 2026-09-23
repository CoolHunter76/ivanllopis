# IvanLlopis.net

Portfolio profesional multilingue construido con FastAPI, Jinja2, Docker y GitHub Actions.

## Entornos

- `develop` se despliega en staging.
- `master` se despliega en produccion.
- `/health` publica estado e identidad de despliegue sin exponer secretos.
- El workflow Uptime Monitor valida periodicamente ambos entornos.

## Desarrollo local

1. Crea y activa un entorno virtual.
2. Instala las dependencias de desarrollo con `pip install -r requirements-dev.txt`.
3. Ejecuta la aplicacion con `uvicorn main:app --reload`.
4. Abre `http://127.0.0.1:8000/es`.

## Calidad

Ejecuta estas validaciones antes de publicar cambios:

```powershell
ruff check .
ruff format --check .
pytest
```

## Operacion y configuracion

- [Guia operativa](docs/OPERATIONS.md)
- [Configuracion y variables](docs/CONFIGURATION.md)
- [Proceso de release](docs/RELEASE.md)

## Seguridad

Los secretos no se versionan. Usa `.env.cv.example` y `compose.secrets.example.yaml` solo como referencias de estructura. Los valores reales deben permanecer fuera del repositorio.
