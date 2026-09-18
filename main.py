import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from assistant import configure_assistant
from seo import configure_seo

BASE = Path(__file__).resolve().parent
SUPPORTED = ("es", "ca", "eu", "en", "fr", "uk", "it", "tr")

app = FastAPI(title="IvanLlopis.net", version="2.0.0")
configure_assistant(app)
configure_seo(app)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def trn(lang_code: str) -> dict:
    language = lang_code if lang_code in SUPPORTED else "es"
    return json.loads((BASE / "translations" / f"{language}.json").read_text(encoding="utf-8"))


def ctx(lang_code: str, **extra: object) -> dict:
    return {
        "lang": lang_code,
        "contact_url": os.getenv("PUBLIC_CONTACT_URL", f"/{lang_code}#profile"),
        "t": trn(lang_code),
        "languages": [{"code": code, **trn(code)["language"]} for code in SUPPORTED],
        **extra,
    }


TECHNOLOGIES = [
    {
        "id": "microsoft",
        "name": "Microsoft",
        "icon": "/static/icons/brands/microsoft.svg",
        "url": "https://www.microsoft.com/",
    },
    {
        "id": "dotnet",
        "name": ".NET",
        "icon": "/static/icons/brands/dotnet.svg",
        "url": "https://dotnet.microsoft.com/",
    },
    {
        "id": "csharp",
        "name": "C#",
        "icon": "/static/icons/brands/csharp.svg",
        "url": "https://learn.microsoft.com/dotnet/csharp/",
    },
    {
        "id": "azure",
        "name": "Microsoft Azure",
        "icon": "/static/icons/brands/azure.svg",
        "url": "https://azure.microsoft.com/",
    },
    {
        "id": "copilot",
        "name": "Microsoft Copilot",
        "icon": "/static/icons/brands/copilot.svg",
        "url": "https://www.microsoft.com/microsoft-copilot/",
    },
    {
        "id": "python",
        "name": "Python",
        "icon": "/static/icons/brands/python.svg",
        "url": "https://www.python.org/",
    },
    {
        "id": "fastapi",
        "name": "FastAPI",
        "icon": "/static/icons/brands/fastapi.svg",
        "url": "https://fastapi.tiangolo.com/",
    },
    {
        "id": "sql",
        "name": "SQL Server",
        "icon": "/static/icons/brands/sql.svg",
        "url": "https://www.microsoft.com/sql-server/",
    },
    {
        "id": "postgresql",
        "name": "PostgreSQL",
        "icon": "/static/icons/brands/postgresql.svg",
        "url": "https://www.postgresql.org/",
    },
    {
        "id": "mongodb",
        "name": "MongoDB",
        "icon": "/static/icons/brands/mongodb.svg",
        "url": "https://www.mongodb.com/",
    },
    {
        "id": "docker",
        "name": "Docker",
        "icon": "/static/icons/brands/docker.svg",
        "url": "https://www.docker.com/",
    },
    {
        "id": "github",
        "name": "GitHub",
        "icon": "/static/icons/brands/github.svg",
        "url": "https://github.com/",
    },
    {
        "id": "github-actions",
        "name": "GitHub Actions",
        "icon": "/static/icons/brands/githubactions.svg",
        "url": "https://github.com/features/actions",
    },
]
AI_ENGINES = [
    {
        "id": "copilot",
        "name": "Microsoft Copilot",
        "icon": "/static/icons/brands/copilot.svg",
        "url": "https://www.microsoft.com/microsoft-copilot/",
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "icon": "/static/icons/brands/openai.svg",
        "url": "https://openai.com/",
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "icon": "/static/icons/brands/anthropic.svg",
        "url": "https://www.anthropic.com/",
    },
    {
        "id": "claude",
        "name": "Claude",
        "icon": "/static/icons/brands/claude.svg",
        "url": "https://claude.ai/",
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "icon": "/static/icons/brands/googlegemini.svg",
        "url": "https://gemini.google.com/",
    },
    {
        "id": "mistral",
        "name": "Mistral AI",
        "icon": "/static/icons/brands/mistralai.svg",
        "url": "https://mistral.ai/",
    },
    {
        "id": "ollama",
        "name": "Ollama",
        "icon": "/static/icons/brands/ollama.svg",
        "url": "https://ollama.com/",
    },
    {
        "id": "llama",
        "name": "Llama",
        "icon": "/static/icons/brands/meta.svg",
        "url": "https://www.llama.com/",
    },
]
HOBBIES = [
    {"id": "swimming", "name": "Natación", "icon": "/static/icons/hobbies/waves.svg"},
    {
        "id": "trekking",
        "name": "Senderismo",
        "icon": "/static/icons/hobbies/mountain.svg",
    },
    {
        "id": "gaming",
        "name": "Videojuegos",
        "icon": "/static/icons/hobbies/gamepad.svg",
    },
    {"id": "drums", "name": "Batería", "icon": "/static/icons/hobbies/drum.svg"},
    {"id": "travel", "name": "Viajes", "icon": "/static/icons/hobbies/plane.svg"},
    {
        "id": "dance",
        "name": "Bailes latinos",
        "icon": "/static/icons/hobbies/music.svg",
    },
]
PROJECTS = [
    {"number": "01", "key": "events", "tags": [".NET", "APIs", "SQL", "Azure"]},
    {"number": "02", "key": "ai", "tags": ["Python", "FastAPI", "Ollama", "Copilot"]},
    {"number": "03", "key": "cloud", "tags": ["Azure", "Docker", "Cloud", "DevOps"]},
    {"number": "04", "key": "portfolio", "tags": ["FastAPI", "i18n", "SEO", "CI/CD"]},
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
        context=ctx(lang, technologies=TECHNOLOGIES, ai_engines=AI_ENGINES, projects=PROJECTS),
    )


@app.get("/{lang}/hobbies", response_class=HTMLResponse, include_in_schema=False)
def hobbies(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/hobbies", status_code=307)
    return templates.TemplateResponse(
        request=request, name="hobbies.html", context=ctx(lang, hobbies=HOBBIES)
    )


@app.get("/{lang}/work-life", response_class=HTMLResponse, include_in_schema=False)
def work_life(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/work-life", status_code=307)
    return templates.TemplateResponse(request=request, name="work_life.html", context=ctx(lang))
