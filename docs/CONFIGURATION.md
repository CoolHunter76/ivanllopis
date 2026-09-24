# Configuracion y variables

Este documento enumera nombres y finalidad. No contiene valores secretos.

## Aplicacion

| Variable | Finalidad | Valor local seguro |
| --- | --- | --- |
| `APP_ENV` | Identidad del entorno publicada por `/health` | `unknown` |
| `APP_VERSION` | Version desplegada | Sobrescritura opcional; por defecto se usa `VERSION` |
| `APP_COMMIT` | SHA Git desplegado | `unknown` |
| `V3_PORTAL_ENABLED` | Activa el portal V3 global | `false` |
| `V3_LANDING_ENABLED` | Compatibilidad temporal con el antiguo flag | `false` |
| `PUBLIC_CONTACT_URL` | Sobrescribe el destino publico de contacto | Ruta local del perfil |

`V3_PORTAL_ENABLED` es el flag principal. `V3_LANDING_ENABLED` se conserva solo como compatibilidad y no debe usarse en configuraciones nuevas.

## Solicitud de CV

| Variable | Finalidad | Sensible |
| --- | --- | --- |
| `RESEND_API_KEY` | Credencial del proveedor de correo | Si |
| `CV_MAIL_FROM` | Remitente autorizado | No, pero depende del dominio |
| `CV_MAIL_TO` | Destinatario de solicitudes | Si |

Los valores reales deben permanecer en el archivo externo configurado por el despliegue y nunca en Git.

## Integracion con GitHub

| Variable | Finalidad | Sensible |
| --- | --- | --- |
| `GITHUB_TOKEN` | Eleva el limite de consultas de Project World | Si |

La aplicacion funciona en modo degradado cuando la API de GitHub no esta disponible.

## Reglas

- No versionar `.env`, `.env.cv` ni variantes locales.
- No copiar secretos en issues, logs, informes o artefactos.
- No incluir valores reales en ejemplos de Compose.
- Rotar inmediatamente cualquier credencial publicada por error.


## Fuente unica de version

La version estable se declara exclusivamente en el archivo `VERSION`, con formato SemVer de tres componentes, por ejemplo `3.0.1`. La aplicacion la usa como version de FastAPI y como valor predeterminado de `/health`. Los scripts de despliegue leen el mismo archivo y exportan `APP_VERSION` para verificar la identidad exacta del contenedor.

`APP_VERSION` se mantiene como una sobrescritura operativa opcional. No debe fijarse de forma permanente en Compose ni duplicarse en el codigo.
