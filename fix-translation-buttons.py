import json
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).resolve().parent / "translations"


def update_translation(path: Path) -> None:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    hero = data.get("hero", {})
    data["buttons"] = [
        hero.get("projects_button", "View projects"),
        hero.get("contact_button", "Contact"),
    ]

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    if not files:
        raise SystemExit(f"No se encontraron traducciones en {TRANSLATIONS_DIR}")

    for path in files:
        update_translation(path)
        print(f"Actualizado: {path.name}")

    print(f"Traducciones actualizadas: {len(files)}")


if __name__ == "__main__":
    main()
