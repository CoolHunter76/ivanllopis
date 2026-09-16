import re
from pathlib import Path

base = Path(__file__).resolve().parents[1]
assistant_path = base / "assistant.py"
css_path = base / "static/css/assistant.css"
icon_path = base / "static/images/meta-ai-icon.png"

for path in (assistant_path, css_path, icon_path):
    if not path.is_file():
        raise SystemExit(f"Falta el archivo requerido: {path}")

assistant = assistant_path.read_text(encoding="utf-8")
powered = (
    '<div class="ai-powered">'
    '<img class="meta-ai-icon" src="/static/images/meta-ai-icon.png?v=1" '
    'alt="" width="20" height="20" loading="lazy">'
    "<span>Powered by Llama 3.2 by Meta</span>"
    "</div>"
)

pattern = r'<div class="ai-powered">.*?</div>'
assistant, count = re.subn(pattern, powered, assistant, count=1, flags=re.DOTALL)
if count == 0:
    marker = '</section><link rel="stylesheet"'
    if marker not in assistant:
        raise SystemExit("No se encontró el punto de inserción de la atribución")
    assistant = assistant.replace(marker, powered + marker, 1)

assistant_path.write_text(assistant, encoding="utf-8", newline="\n")

marker = "/* Meta AI mini icon */"
css = css_path.read_text(encoding="utf-8")
if marker in css:
    css = css[: css.index(marker)].rstrip() + "\n"
css += """

/* Meta AI mini icon */
.ai-powered {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.45rem !important;
    width: 100% !important;
    padding: 0.4rem 1rem 0.75rem !important;
    box-sizing: border-box !important;
    text-align: center !important;
}

.meta-ai-icon {
    display: block !important;
    flex: 0 0 20px !important;
    width: 20px !important;
    height: 20px !important;
    max-width: 20px !important;
    max-height: 20px !important;
    object-fit: contain !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}
"""
css_path.write_text(css, encoding="utf-8", newline="\n")

print("Icono visual y atribución actualizados correctamente.")
