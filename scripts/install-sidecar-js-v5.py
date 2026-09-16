from pathlib import Path

base = Path(__file__).resolve().parents[1]
js_path = base / "static/js/assistant.js"
patch_path = base / "static/assistant-sidecar-v5.js"
if not js_path.is_file() or not patch_path.is_file():
    raise SystemExit("Falta assistant.js o assistant-sidecar-v5.js")
js = js_path.read_text(encoding="utf-8")
marker = 'shell.dataset.sidecarReady = "true"'
if marker not in js:
    js += "\n" + patch_path.read_text(encoding="utf-8")
js_path.write_text(js, encoding="utf-8", newline="\n")
print("Control de apertura/cierre del sidecar instalado.")
