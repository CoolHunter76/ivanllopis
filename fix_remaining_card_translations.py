from __future__ import annotations

import json
from pathlib import Path

TRANSLATIONS_DIR = Path("translations")

REPLACEMENTS = {
    "en": {
        "Plataforma de eventos": "Event platform",
        "Gestión de eventos, talleres, asistentes y operaciones.": "Management of events, workshops, attendees and operations.",
        "Gestión de eventos": "Event management",
        "Agentes de IA": "AI agents",
        "Asistentes, conocimiento controlado y modelos locales.": "Assistants, controlled knowledge and local models.",
        "Asistentes, conocimiento controlado": "Assistants, controlled knowledge",
        "Patrones de arquitectura, automatización y despliegue.": "Architecture patterns, automation and deployment.",
        "Patrones de arquitectura": "Architecture patterns",
        "Claridad, construcción": "Clarity, implementation",
        "Natación": "Swimming",
        "Senderismo": "Hiking",
        "Videojuegos": "Video games",
        "Volver a la página principal": "Back to the home page",
    },
    "fr": {
        "Plataforma de eventos": "Plateforme événementielle",
        "Gestión de eventos, talleres, asistentes y operaciones.": "Gestion des événements, des ateliers, des participants et des opérations.",
        "Gestión de eventos": "Gestion d’événements",
        "Agentes de IA": "Agents d’IA",
        "Asistentes, conocimiento controlado y modelos locales.": "Assistants, connaissances contrôlées et modèles locaux.",
        "Asistentes, conocimiento controlado": "Assistants, connaissances contrôlées",
        "Patrones de arquitectura, automatización y despliegue.": "Modèles d’architecture, automatisation et déploiement.",
        "Patrones de arquitectura": "Modèles d’architecture",
        "Claridad, construcción": "Clarté, réalisation",
        "Natación": "Natation",
        "Senderismo": "Randonnée",
        "Videojuegos": "Jeux vidéo",
        "Volver a la página principal": "Retour à la page d’accueil",
    },
    "uk": {
        "Plataforma de eventos": "Платформа для подій",
        "Gestión de eventos, talleres, asistentes y operaciones.": "Керування подіями, майстер-класами, учасниками та операціями.",
        "Gestión de eventos": "Керування подіями",
        "Agentes de IA": "Агенти ШІ",
        "Asistentes, conocimiento controlado y modelos locales.": "Асистенти, контрольовані знання та локальні моделі.",
        "Asistentes, conocimiento controlado": "Асистенти, контрольовані знання",
        "Patrones de arquitectura, automatización y despliegue.": "Архітектурні шаблони, автоматизація та розгортання.",
        "Patrones de arquitectura": "Архітектурні шаблони",
        "Claridad, construcción": "Ясність, реалізація",
        "Natación": "Плавання",
        "Senderismo": "Піші походи",
        "Videojuegos": "Відеоігри",
        "Volver a la página principal": "Повернутися на головну сторінку",
    },
    "it": {
        "Plataforma de eventos": "Piattaforma per eventi",
        "Gestión de eventos, talleres, asistentes y operaciones.": "Gestione di eventi, workshop, partecipanti e operazioni.",
        "Gestión de eventos": "Gestione degli eventi",
        "Agentes de IA": "Agenti IA",
        "Asistentes, conocimiento controlado y modelos locales.": "Assistenti, conoscenza controllata e modelli locali.",
        "Asistentes, conocimiento controlado": "Assistenti, conoscenza controllata",
        "Patrones de arquitectura, automatización y despliegue.": "Pattern architetturali, automazione e distribuzione.",
        "Patrones de arquitectura": "Pattern architetturali",
        "Claridad, construcción": "Chiarezza, realizzazione",
        "Natación": "Nuoto",
        "Senderismo": "Escursionismo",
        "Videojuegos": "Videogiochi",
        "Volver a la página principal": "Torna alla pagina principale",
    },
    "tr": {
        "Plataforma de eventos": "Etkinlik platformu",
        "Gestión de eventos, talleres, asistentes y operaciones.": "Etkinliklerin, atölyelerin, katılımcıların ve operasyonların yönetimi.",
        "Gestión de eventos": "Etkinlik yönetimi",
        "Agentes de IA": "Yapay zekâ ajanları",
        "Asistentes, conocimiento controlado y modelos locales.": "Asistanlar, kontrollü bilgi ve yerel modeller.",
        "Asistentes, conocimiento controlado": "Asistanlar, kontrollü bilgi",
        "Patrones de arquitectura, automatización y despliegue.": "Mimari kalıplar, otomasyon ve dağıtım.",
        "Patrones de arquitectura": "Mimari kalıplar",
        "Claridad, construcción": "Netlik, uygulama",
        "Natación": "Yüzme",
        "Senderismo": "Doğa yürüyüşü",
        "Videojuegos": "Video oyunları",
        "Volver a la página principal": "Ana sayfaya dön",
    },
}


def replace_values(value: object, replacements: dict[str, str]) -> object:
    if isinstance(value, dict):
        return {key: replace_values(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_values(item, replacements) for item in value]
    if isinstance(value, str):
        result = value
        for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            result = result.replace(old, new)
        return result
    return value


def main() -> None:
    updated = 0
    for language, replacements in REPLACEMENTS.items():
        path = TRANSLATIONS_DIR / f"{language}.json"
        if not path.exists():
            raise FileNotFoundError(f"No existe {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        translated = replace_values(data, replacements)
        path.write_text(
            json.dumps(translated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"Actualizado: {path}")
        updated += 1
    print(f"Archivos actualizados: {updated}")


if __name__ == "__main__":
    main()
