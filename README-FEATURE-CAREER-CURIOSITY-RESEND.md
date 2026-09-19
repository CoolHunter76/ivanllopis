# Feature: Career curiosity + Resend premium

Mejora la conversión de Vida laboral y Solicitud de CV mediante persuasión ética: curiosidad, contexto, progressive disclosure, señales de confianza y reducción de fricción. No usa urgencia falsa, presión, escasez artificial ni dark patterns.

## Incluye
- Nueva narrativa y CTAs en `work-life`.
- Formulario contextual y confirmación visual accesible.
- Email HTML para el propietario y acuse de recibo para el solicitante.
- Reply-To, versión de texto y escape HTML del contenido del usuario.
- Mantiene honeypot, consentimiento, validación y rate limit existentes.
- Traducciones nuevas en español e inglés; los demás idiomas mantienen la misma estructura y usan copy inglés neutro para las claves nuevas.

## Resend
Los secretos NO están incluidos. En el VPS deben existir `RESEND_API_KEY`, `CV_MAIL_FROM` y `CV_MAIL_TO` dentro del entorno del contenedor.

## Staging
El staging debe seguir publicándose únicamente en `127.0.0.1:8001`. No modificar producción en `8000`.

## Validación
```text
ruff check .
ruff format --check .
pytest
```
