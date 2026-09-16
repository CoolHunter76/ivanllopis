import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from seo import configure_seo

BASE = Path(__file__).resolve().parent
SUPPORTED = ("es", "ca", "eu", "en", "fr", "uk", "it", "tr")

app = FastAPI(title="IvanLlopis.net", version="1.8.0")
configure_seo(app)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def trn(lang_code: str) -> dict:
    selected_language = lang_code if lang_code in SUPPORTED else "es"
    translation_file = BASE / "translations" / f"{selected_language}.json"
    return json.loads(translation_file.read_text(encoding="utf-8"))


def ctx(lang_code: str, **extra: object) -> dict:
    return {
        "lang": lang_code,
        "t": trn(lang_code),
        "language_data": {code: trn(code) for code in SUPPORTED},
        **extra,
    }


TECH = [
    ("microsoft.svg", "Microsoft"),
    ("dotnet.svg", ".NET / C#"),
    ("azure.svg", "Azure"),
    ("copilot.svg", "Copilot"),
    ("python.svg", "Python"),
    ("fastapi.svg", "FastAPI"),
    ("sql.svg", "SQL Server"),
    ("postgresql.svg", "PostgreSQL"),
    ("mongodb.svg", "MongoDB"),
    ("docker.svg", "Docker"),
]

AI = [
    ("copilot.svg", "Microsoft Copilot"),
    ("chatgpt.svg", "OpenAI ChatGPT"),
    ("claude.svg", "Claude"),
    ("gemini.svg", "Google Gemini"),
    ("mistral.svg", "Mistral AI"),
]

PROJECTS = [
    ("01", "Plataforma de eventos", [".NET", "APIs", "SQL", "Azure"]),
    ("02", "Agentes de IA", ["Python", "FastAPI", "Ollama", "Copilot"]),
    ("03", "Arquitecturas cloud", ["Azure", "Docker", "Cloud", "DevOps"]),
]

HOBBIES = [
    ("ðŸŠ", "Swimming"),
    ("ðŸ¥¾", "Trekking"),
    ("ðŸŽ®", "Gaming"),
    ("ðŸ¥", "Drums"),
    ("âœˆï¸", "Travel"),
    ("ðŸ’ƒ", "Latin Dance"),
]


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok", "languages": SUPPORTED}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/es", status_code=307)


@app.get("/{lang}", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es", status_code=307)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=ctx(
            lang,
            technologies=TECH,
            ai_engines=AI,
            projects=PROJECTS,
        ),
    )


@app.get("/{lang}/hobbies", response_class=HTMLResponse, include_in_schema=False)
def hobbies(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/hobbies", status_code=307)

    return templates.TemplateResponse(
        request=request,
        name="hobbies.html",
        context=ctx(lang, hobbies=HOBBIES),
    )
