# Proceso de release

## Flujo de ramas

- Las funcionalidades parten de `develop`.
- Las correcciones usan el prefijo `bugfix/`.
- Los cambios se integran en `develop` mediante Pull Request.
- Staging valida `develop` antes de promover a `master`.
- Produccion se despliega exclusivamente desde `master`.

## Criterios de promocion

Antes de crear una release estable:

1. El arbol de trabajo esta limpio.
2. `develop` coincide con `origin/develop`.
3. Ruff lint y format finalizan correctamente.
4. La suite completa finaliza correctamente.
5. CD Staging finaliza correctamente.
6. `/health` de staging publica el commit esperado.
7. Uptime Monitor finaliza correctamente y genera su artefacto.
8. No existen respaldos, informes temporales ni instaladores puntuales versionados.
9. La documentacion operativa refleja el comportamiento actual.

## Promocion a produccion

1. Crea un Pull Request de `develop` hacia `master`.
2. Espera todos los checks obligatorios.
3. Fusiona sin omitir las protecciones de rama.
4. Espera CD Production.
5. Comprueba `/health` en produccion.
6. Ejecuta Uptime Monitor sobre el estado publicado.
7. Crea la etiqueta estable solo cuando toda la validacion sea correcta.

Etiqueta prevista para este cierre:

```text
v3.0.1
```

## Reversion

Si produccion falla, restaura mediante Git un commit conocido y vuelve a ejecutar el despliegue autorizado. No uses cambios manuales dentro del contenedor como solucion permanente. Documenta la causa y aplica la correccion desde una rama `bugfix/`.
