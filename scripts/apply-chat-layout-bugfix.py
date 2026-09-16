from pathlib import Path

base = Path(__file__).resolve().parents[1]
assistant_path = base / "assistant.py"
css_path = base / "static" / "css" / "assistant.css"
bugfix_css_path = base / "static" / "chat-layout-bugfix.css"

for path in (assistant_path, css_path, bugfix_css_path):
    if not path.is_file():
        raise SystemExit(f"Falta el archivo requerido: {path}")

assistant = assistant_path.read_text(encoding="utf-8")

# Remove the broken visual companion from page content.
start_marker = '<div class="ai-companion"'
while start_marker in assistant:
    start = assistant.index(start_marker)
    image_end = assistant.find("</div>", start)
    if image_end < 0:
        raise SystemExit("No se pudo localizar el cierre de ai-companion en assistant.py")
    assistant = assistant[:start] + assistant[image_end + len("</div>") :]

# Ensure a visible accessible close button exists inside the chat header.
if 'id="ai-close"' not in assistant:
    header_marker = '<header><strong>Asistente de Ivan</strong>'
    replacement = header_marker + '<button id="ai-close" type="button" aria-label="Cerrar asistente" title="Cerrar">&#215;</button>'
    if header_marker not in assistant:
        raise SystemExit("No se encontró la cabecera del chat para añadir el botón de cierre")
    assistant = assistant.replace(header_marker, replacement, 1)
else:
    assistant = assistant.replace('id="ai-close" aria-label="Cerrar"', 'id="ai-close" type="button" aria-label="Cerrar asistente" title="Cerrar"')

assistant_path.write_text(assistant, encoding="utf-8", newline="\n")

bugfix_css = bugfix_css_path.read_text(encoding="utf-8")
current_css = css_path.read_text(encoding="utf-8")
marker = "/* Sprint 9 bugfix: background belongs only to the chat panel. */"
if marker in current_css:
    current_css = current_css[: current_css.index(marker)].rstrip() + "\n"
css_path.write_text(current_css + "\n" + bugfix_css, encoding="utf-8", newline="\n")

print("Bugfix aplicado: imagen limitada al fondo del chat y botón X restaurado.")
