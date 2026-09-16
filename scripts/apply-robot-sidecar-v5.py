import re
from pathlib import Path

base = Path(__file__).resolve().parents[1]
assistant_path = base / "assistant.py"
css_path = base / "static/css/assistant.css"
patch_css_path = base / "static/robot-sidecar-v5.css"
image_path = base / "static/images/ai-robot-sidecar.webp"

for path in (assistant_path, css_path, patch_css_path, image_path):
    if not path.is_file():
        raise SystemExit(f"Falta el archivo requerido: {path}")

assistant = assistant_path.read_text(encoding="utf-8")

# Remove visual experiments from earlier versions.
assistant = re.sub(
    r'<div class="ai-companion"[^>]*>.*?</div>',
    "",
    assistant,
    flags=re.DOTALL,
)
assistant = re.sub(
    r'<div class="ai-chat-shell"[^>]*>.*?</div>\s*(?=<button id="ai-toggle")',
    "",
    assistant,
    flags=re.DOTALL,
)

panel_start = assistant.find('<section id="ai-panel"')
if panel_start < 0:
    raise SystemExit("No se encontró el panel #ai-panel en assistant.py")
panel_end = assistant.find("</section>", panel_start)
if panel_end < 0:
    raise SystemExit("No se encontró el cierre del panel #ai-panel")
panel_end += len("</section>")
panel = assistant[panel_start:panel_end]

# Make sure the popup header contains title and close button.
header = (
    '<header class="ai-header"><div class="ai-title-wrap">'
    '<strong class="ai-title">Asistente de Ivan</strong>'
    '<span class="ai-subtitle">IA local - Información pública</span></div>'
    '<button id="ai-close" type="button" aria-label="Cerrar asistente" '
    'title="Cerrar">&#215;</button></header>'
)
panel, count = re.subn(
    r'<header(?: class="[^"]*")?>.*?</header>',
    header,
    panel,
    count=1,
    flags=re.DOTALL,
)
if count != 1:
    raise SystemExit("No se pudo reconstruir la cabecera interna del chat")

shell = (
    '<div id="ai-chat-shell" class="ai-chat-shell" hidden>'
    '<aside class="ai-chat-sidecar" aria-label="Presentación visual del asistente">'
    '<img src="/static/images/ai-robot-sidecar.webp" '
    'alt="Asistente robótico junto a un mensaje de presentación" loading="lazy">'
    "</aside>"
    f"{panel}"
    "</div>"
)
assistant = assistant[:panel_start] + shell + assistant[panel_end:]
assistant_path.write_text(assistant, encoding="utf-8", newline="\n")

current_css = css_path.read_text(encoding="utf-8")
marker = "/* Sprint 9 v5: robot sidecar shown only while the assistant is open. */"
if marker in current_css:
    current_css = current_css[: current_css.index(marker)].rstrip() + "\n"
css_path.write_text(
    current_css + "\n" + patch_css_path.read_text(encoding="utf-8"),
    encoding="utf-8",
    newline="\n",
)

print("Bugfix v5 aplicado: robot y mensaje a la izquierda del chat, sin invadir la página.")
