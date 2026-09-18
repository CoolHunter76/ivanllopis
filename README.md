# Logos de empresas - placeholders

Los siete SVG de `static/images/companies/` son archivos SVG válidos pero intencionadamente vacíos.

Reemplázalos manualmente conservando exactamente estos nombres:
- hp.svg
- repsol.svg
- mapfre.svg
- adif.svg
- energyavm.svg
- capgemini.svg
- sogeti.svg

## Integración
1. Copia `static/images/companies/` al proyecto.
2. Copia `static/css/companies.css` o integra sus reglas en `static/css/site.css`.
3. Copia `templates/companies.html` e inclúyelo desde la landing donde corresponda.
4. Sustituye cada SVG vacío por el logo oficial manteniendo el mismo nombre.

El HTML usa `url_for('static', ...)` para evitar rutas absolutas rígidas.
