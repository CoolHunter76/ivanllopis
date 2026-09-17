import json
from pathlib import Path

LANGUAGES = ("ca", "eu", "en", "fr", "uk", "it", "tr")
SPANISH_CARD_PHRASES = (
    "Plataforma de eventos", "Gestión de eventos", "Agentes de IA",
    "Asistentes, conocimiento controlado", "Patrones de arquitectura",
    "Claridad, construcción", "Natación", "Senderismo", "Videojuegos",
    "Volver a la página principal",
)

def test_non_spanish_locales_do_not_reuse_spanish_cards():
    for language in LANGUAGES:
        text = Path(f"translations/{language}.json").read_text(encoding="utf-8")
        for phrase in SPANISH_CARD_PHRASES:
            assert phrase not in text, f"{language}: {phrase}"

def test_all_translation_files_share_recursive_structure():
    structures = []
    for path in sorted(Path("translations").glob("*.json")):
        structures.append(_shape(json.loads(path.read_text(encoding="utf-8"))))
    assert len(set(structures)) == 1

def _shape(value):
    if isinstance(value, dict):
        return tuple((key, _shape(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_shape(item) for item in value)
    return type(value).__name__
