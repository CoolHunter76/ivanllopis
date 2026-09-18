import json
import os
import re
import smtplib
import ssl
import time
from collections import defaultdict, deque
from email.message import EmailMessage
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from assistant import configure_assistant
from seo import configure_seo

BASE = Path(__file__).resolve().parent
SUPPORTED = ("es", "ca", "gl", "oc", "eu", "en", "fr", "uk", "it", "tr", "ru", "zh-Hans", "ja")

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


CLIENT_EXPERIENCES = [
    {
        "id": "hp",
        "name": "HP Hewlett-Packard",
        "logo": "/static/images/companies/hp.svg",
        "url": "https://www.hp.com/",
        "technologies": ["React", "JavaScript", "Azure DevOps"],
    },
    {
        "id": "repsol",
        "name": "Repsol",
        "logo": "/static/images/companies/repsol.svg",
        "url": "https://www.repsol.com/",
        "technologies": ["Scripting", "Data anonymization"],
    },
    {
        "id": "mapfre",
        "name": "MAPFRE",
        "logo": "/static/images/companies/mapfre.svg",
        "url": "https://www.mapfre.com/",
        "technologies": ["Azure Functions", ".NET", "C#"],
    },
    {
        "id": "adif",
        "name": "ADIF",
        "logo": "/static/images/companies/adif.svg",
        "url": "https://www.adif.es/",
        "technologies": ["Microsoft Azure", "Cybersecurity", "Hardening"],
    },
    {
        "id": "energyavm",
        "name": "EnergyaVM",
        "logo": "/static/images/companies/energyavm.svg",
        "url": "https://www.energyavm.es/",
        "technologies": [".NET", "C#", "REST API", "GitLab"],
    },
]

PAGE_TEMPLATES = {
    "profile": "profile.html",
    "capabilities": "capabilities.html",
    "technologies": "technologies.html",
    "projects": "projects.html",
}

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
CV_REQUESTS_BY_IP: dict[str, deque[float]] = defaultdict(deque)


class CvRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254)
    phone: str = Field(default="", max_length=40)
    message: str = Field(min_length=10, max_length=1500)
    consent: bool
    website: str = Field(default="", max_length=200)
    language: str = Field(default="es", max_length=5)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def _check_cv_rate_limit(request: Request) -> None:
    now = time.monotonic()
    queue = CV_REQUESTS_BY_IP[_client_ip(request)]
    while queue and queue[0] < now - 3600:
        queue.popleft()
    if len(queue) >= 3:
        raise HTTPException(429, "Too many CV requests. Please try again later.")
    queue.append(now)


def send_cv_request(body: CvRequest) -> None:
    host = os.getenv("CV_SMTP_HOST", "smtp.ionos.es")
    port = int(os.getenv("CV_SMTP_PORT", "465"))
    username = os.getenv("CV_SMTP_USERNAME", "contact@ivanllopis.net")
    password = os.getenv("CV_SMTP_PASSWORD", "")
    sender = os.getenv("CV_MAIL_FROM", username)
    recipient = os.getenv("CV_MAIL_TO", "cv@ivanllopis.net")
    if not all((host, username, password, sender, recipient)):
        raise RuntimeError("CV email service is not configured")

    message = EmailMessage()
    message["Subject"] = "New CV request - IvanLlopis.net"
    message["From"] = sender
    message["To"] = recipient
    message["Reply-To"] = body.email
    message.set_content(
        "New CV request\n\n"
        f"Name or company: {body.name}\n"
        f"Email: {body.email}\n"
        f"Phone: {body.phone or 'Not provided'}\n"
        f"Language: {body.language}\n\n"
        f"Message:\n{body.message}\n"
    )
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)


@app.post("/api/cv-request", include_in_schema=False)
def create_cv_request(body: CvRequest, request: Request) -> dict[str, str]:
    if body.website:
        raise HTTPException(400, "Invalid request")
    if not body.consent:
        raise HTTPException(422, "Privacy consent is required")
    if not EMAIL_PATTERN.fullmatch(body.email.strip()):
        raise HTTPException(422, "A valid email address is required")
    if body.language not in SUPPORTED:
        raise HTTPException(422, "Unsupported language")
    _check_cv_rate_limit(request)
    try:
        send_cv_request(body)
    except (OSError, RuntimeError, smtplib.SMTPException) as error:
        raise HTTPException(503, "The CV request could not be sent") from error
    return {"status": "sent"}


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


@app.get("/{lang}/profile", response_class=HTMLResponse, include_in_schema=False)
def profile(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/profile", status_code=307)
    return templates.TemplateResponse(request=request, name="profile.html", context=ctx(lang))


@app.get("/{lang}/capabilities", response_class=HTMLResponse, include_in_schema=False)
def capabilities(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/capabilities", status_code=307)
    return templates.TemplateResponse(request=request, name="capabilities.html", context=ctx(lang))


@app.get("/{lang}/technologies", response_class=HTMLResponse, include_in_schema=False)
def technologies(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/technologies", status_code=307)
    return templates.TemplateResponse(
        request=request,
        name="technologies.html",
        context=ctx(lang, technologies=TECHNOLOGIES, ai_engines=AI_ENGINES),
    )


@app.get("/{lang}/projects", response_class=HTMLResponse, include_in_schema=False)
def projects(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/projects", status_code=307)
    return templates.TemplateResponse(
        request=request, name="projects.html", context=ctx(lang, projects=PROJECTS)
    )


@app.get("/{lang}/work-life", response_class=HTMLResponse, include_in_schema=False)
def work_life(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/work-life", status_code=307)
    return templates.TemplateResponse(
        request=request, name="work_life.html", context=ctx(lang, experiences=CLIENT_EXPERIENCES)
    )


@app.get("/{lang}/request-cv", response_class=HTMLResponse, include_in_schema=False)
def request_cv(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/request-cv", status_code=307)
    return templates.TemplateResponse(request=request, name="request_cv.html", context=ctx(lang))


@app.get("/{lang}/privacy", response_class=HTMLResponse, include_in_schema=False)
def privacy(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/privacy", status_code=307)
    return templates.TemplateResponse(request=request, name="privacy.html", context=ctx(lang))


@app.get("/{lang}/hobbies", response_class=HTMLResponse, include_in_schema=False)
def hobbies(request: Request, lang: str):
    if lang not in SUPPORTED:
        return RedirectResponse("/es/hobbies", status_code=307)
    return templates.TemplateResponse(
        request=request, name="hobbies.html", context=ctx(lang, hobbies=HOBBIES)
    )
