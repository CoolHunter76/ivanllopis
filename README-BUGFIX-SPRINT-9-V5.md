# Bugfix Sprint 9 v5: robot lateral

El robot y el mensaje de presentación aparecen a la izquierda del chat únicamente cuando el chat está abierto. Ambos forman un único componente flotante y no alteran la página principal.

En pantallas de 900 px o menos se oculta la ilustración y se conserva únicamente el chat.

## Aplicación

```powershell
python .\scripts\apply-robot-sidecar-v5.py
python .\scripts\install-sidecar-js-v5.py
```

Después ejecuta Ruff, formato y pytest. Los scripts de este paquete ya están formateados y validados.
