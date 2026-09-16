from pathlib import Path

base = Path(__file__).resolve().parents[1]
assistant_path = base / "assistant.py"
css_path = base / "static" / "css" / "assistant.css"

if not assistant_path.exists() or not css_path.exists():
    raise SystemExit(
        "Ejecuta este script desde un paquete descomprimido en la raíz del repositorio."
    )

assistant = assistant_path.read_text(encoding="utf-8")
css_additions = (base / "static" / "css-assistant-visual-additions.css").read_text(encoding="utf-8")

companion = '<div class="ai-companion" aria-hidden="true"><img src="/static/images/ai-assistant-companion.webp" alt="" loading="lazy"></div>'
powered = '<div class="ai-powered"><span class="ai-powered-mark" aria-hidden="true">L</span><a href="https://www.llama.com/" target="_blank" rel="noopener noreferrer">Powered by Llama 3.2 by Meta</a></div>'

if "ai-assistant-companion.webp" not in assistant:
    marker = '<section id="ai-panel"'
    position = assistant.find(marker)
    if position < 0:
        raise SystemExit("No se encontró el panel del asistente en assistant.py.")
    assistant = assistant[:position] + companion + assistant[position:]

if "Powered by Llama 3.2 by Meta" not in assistant:
    marker = '</section><link rel="stylesheet"'
    if marker not in assistant:
        raise SystemExit("No se encontró el final del panel del asistente en assistant.py.")
    assistant = assistant.replace(marker, powered + marker, 1)

if ".ai-companion{" not in css_path.read_text(encoding="utf-8"):
    with css_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\n" + css_additions)

assistant_path.write_text(assistant, encoding="utf-8", newline="\n")
print("Visual del asistente y atribución Llama integrados correctamente.")
