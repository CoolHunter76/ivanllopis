import json
import os
import re
import time
from collections import defaultdict, deque
from html import escape
from pathlib import Path

import resend
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from resend.exceptions import ResendError

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
        "id": "invercaixa",
        "name": "InverCaixa · CaixaBank Asset Management",
        "logo": "/static/images/companies/caixabank.svg",
        "context_logo": "/static/images/companies/caixabank.svg",
        "url": "https://www.caixabankassetmanagement.com/",
        "technologies": [
            ".NET Framework",
            "SQL Server",
            "SICAV",
            "Relational Databases",
            "Functional analysis",
        ],
    },
    {
        "id": "fundacion_caixa",
        "name": "Fundación ”la Caixa”",
        "logo": "/static/images/companies/fundacion-la-caixa.svg",
        "context_logo": "/static/images/companies/caixabank.svg",
        "url": "https://fundacionlacaixa.org/",
        "technologies": [
            "C#",
            "VB.NET",
            ".NET Framework 3.5",
            "MVC",
            "ASP.NET",
            "jQuery",
            "SQL Server 2008",
            "Relational Databases",
        ],
    },
    {
        "id": "servihabitat",
        "name": "SILK · Servihabitat",
        "logo": "/static/images/companies/servihabitat.svg",
        "context_logo": "/static/images/companies/caixabank.svg",
        "url": "https://www.servihabitat.com/",
        "technologies": [
            "C#",
            "VB.NET",
            ".NET Framework 3.5",
            "ASP.NET",
            "SQL Server 2008",
            "SSIS",
            "Relational Databases",
        ],
    },
    {
        "id": "food_sector",
        "name": "Sector alimentación",
        "logo": "/static/images/companies/idilia-foods.webp",
        "url": "https://idilia.es/",
        "technologies": [
            "C#",
            ".NET Framework",
            "ASP.NET",
            "MVC",
            "jQuery",
            "PL/SQL",
            "SQL Server",
            "Relational Databases",
        ],
    },
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

EMAIL_COPY = {
    "es": (
        "Nueva solicitud de CV - IvanLlopis.net",
        "Nueva solicitud de CV",
        "Contacto profesional recibido desde el formulario de solicitud de CV.",
        "Nombre / empresa",
        "Correo electrónico",
        "Teléfono",
        "Idioma",
        "Mensaje",
        "Solicitud de CV recibida - IvanLlopis.net",
        "Solicitud recibida",
        "Tu solicitud se ha recibido correctamente. Responderé al correo facilitado.",
        "Gracias por tu interés en mi perfil profesional.",
    ),
    "ca": (
        "Nova sol·licitud de CV - IvanLlopis.net",
        "Nova sol·licitud de CV",
        "Contacte professional rebut des del formulari de sol·licitud del CV.",
        "Nom / empresa",
        "Correu electrònic",
        "Telèfon",
        "Idioma",
        "Missatge",
        "Sol·licitud de CV rebuda - IvanLlopis.net",
        "Sol·licitud rebuda",
        "La teva sol·licitud s'ha rebut correctament. Respondré al correu facilitat.",
        "Gràcies pel teu interès en el meu perfil professional.",
    ),
    "en": (
        "New CV request - IvanLlopis.net",
        "New CV request",
        "Professional contact received through the CV request form.",
        "Name / company",
        "Email",
        "Phone",
        "Language",
        "Message",
        "CV request received - IvanLlopis.net",
        "Request received",
        "Your request has been received successfully. I will reply to the email address provided.",
        "Thank you for your interest in my professional profile.",
    ),
    "fr": (
        "Nouvelle demande de CV - IvanLlopis.net",
        "Nouvelle demande de CV",
        "Contact professionnel reçu via le formulaire de demande de CV.",
        "Nom / entreprise",
        "E-mail",
        "Téléphone",
        "Langue",
        "Message",
        "Demande de CV reçue - IvanLlopis.net",
        "Demande reçue",
        "Votre demande a bien été reçue. Je répondrai à l'adresse e-mail indiquée.",
        "Merci de votre intérêt pour mon profil professionnel.",
    ),
    "gl": (
        "Nova solicitude de CV - IvanLlopis.net",
        "Nova solicitude de CV",
        "Contacto profesional recibido desde o formulario de solicitude do CV.",
        "Nome / empresa",
        "Correo electrónico",
        "Teléfono",
        "Idioma",
        "Mensaxe",
        "Solicitude de CV recibida - IvanLlopis.net",
        "Solicitude recibida",
        "A túa solicitude recibiuse correctamente. Responderei ao correo facilitado.",
        "Grazas polo teu interese no meu perfil profesional.",
    ),
    "oc": (
        "Naua sollicitud de CV - IvanLlopis.net",
        "Naua sollicitud de CV",
        "Contacte professionau recebut deth formulari de sollicitud deth CV.",
        "Nòm / entrepresa",
        "Corrèu electronic",
        "Telefòn",
        "Lengua",
        "Messatge",
        "Sollicitud de CV recebut - IvanLlopis.net",
        "Sollicitud recebut",
        "Era tua sollicitud s'a recebut corrèctament. Responerè ath corrèu facilitat.",
        "Gràcies peth tòn interès en mèn perfil professionau.",
    ),
    "eu": (
        "CV eskaera berria - IvanLlopis.net",
        "CV eskaera berria",
        "CV eskaera formulariotik jasotako harreman profesionala.",
        "Izena / enpresa",
        "Helbide elektronikoa",
        "Telefonoa",
        "Hizkuntza",
        "Mezua",
        "CV eskaera jaso da - IvanLlopis.net",
        "Eskaera jasota",
        "Zure eskaera behar bezala jaso da. Emandako helbide elektronikora erantzungo dut.",
        "Eskerrik asko nire profil profesionalean interesa izateagatik.",
    ),
    "it": (
        "Nuova richiesta CV - IvanLlopis.net",
        "Nuova richiesta CV",
        "Contatto professionale ricevuto tramite il modulo di richiesta CV.",
        "Nome / azienda",
        "E-mail",
        "Telefono",
        "Lingua",
        "Messaggio",
        "Richiesta CV ricevuta - IvanLlopis.net",
        "Richiesta ricevuta",
        "La richiesta è stata ricevuta correttamente. Risponderò all'indirizzo e-mail indicato.",
        "Grazie per l'interesse nel mio profilo professionale.",
    ),
    "tr": (
        "Yeni CV talebi - IvanLlopis.net",
        "Yeni CV talebi",
        "CV talep formu üzerinden profesyonel iletişim alındı.",
        "Ad / şirket",
        "E-posta",
        "Telefon",
        "Dil",
        "Mesaj",
        "CV talebi alındı - IvanLlopis.net",
        "Talep alındı",
        "Talebiniz başarıyla alındı. Verdiğiniz e-posta adresine yanıt vereceğim.",
        "Profesyonel profilime gösterdiğiniz ilgi için teşekkür ederim.",
    ),
    "uk": (
        "Новий запит CV - IvanLlopis.net",
        "Новий запит CV",
        "Професійний контакт отримано через форму запиту CV.",
        "Ім’я / компанія",
        "Електронна пошта",
        "Телефон",
        "Мова",
        "Повідомлення",
        "Запит CV отримано - IvanLlopis.net",
        "Запит отримано",
        "Ваш запит успішно отримано. Я відповім на вказану електронну адресу.",
        "Дякую за інтерес до мого професійного профілю.",
    ),
    "ru": (
        "Новый запрос CV - IvanLlopis.net",
        "Новый запрос CV",
        "Профессиональный запрос получен через форму CV.",
        "Имя / компания",
        "Электронная почта",
        "Телефон",
        "Язык",
        "Сообщение",
        "Запрос CV получен - IvanLlopis.net",
        "Запрос получен",
        "Ваш запрос успешно получен. Я отвечу на указанный адрес электронной почты.",
        "Спасибо за интерес к моему профессиональному профилю.",
    ),
    "zh-Hans": (
        "新的简历申请 - IvanLlopis.net",
        "新的简历申请",
        "已通过简历申请表收到专业联系信息。",
        "姓名 / 公司",
        "电子邮件",
        "电话",
        "语言",
        "留言",
        "已收到简历申请 - IvanLlopis.net",
        "申请已收到",
        "您的申请已成功收到。我会回复您提供的电子邮件地址。",
        "感谢您对我的专业资料感兴趣。",
    ),
    "ja": (
        "新しいCVリクエスト - IvanLlopis.net",
        "新しいCVリクエスト",
        "CVリクエストフォームからプロフェッショナルなお問い合わせを受け取りました。",
        "氏名 / 会社",
        "メール",
        "電話",
        "言語",
        "メッセージ",
        "CVリクエストを受信しました - IvanLlopis.net",
        "リクエストを受信しました",
        "リクエストを正常に受信しました。ご入力いただいたメールアドレスに返信します。",
        "プロフィールにご関心をお寄せいただきありがとうございます。",
    ),
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
    language: str = Field(default="es", max_length=7)


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


def _email_copy(language: str) -> dict[str, str]:
    copies = {
        "es": {
            "admin_subject": "Nueva solicitud de CV - IvanLlopis.net",
            "receipt_subject": "He recibido tu solicitud - IvanLlopis.net",
            "receipt_title": "Solicitud recibida",
            "receipt_text": "Gracias por tu interés profesional. He recibido tu solicitud y responderé personalmente al correo facilitado.",
        },
        "en": {
            "admin_subject": "New CV request - IvanLlopis.net",
            "receipt_subject": "Your request has been received - IvanLlopis.net",
            "receipt_title": "Request received",
            "receipt_text": "Thank you for your professional interest. Your request has been received and I will reply personally to the email provided.",
        },
    }
    return copies.get(language, copies["en"])


def _email_shell(title: str, intro: str, content: str) -> str:
    return f"""<!doctype html><html><body style="margin:0;background:#060a08;color:#effff3;font-family:Arial,sans-serif"><div style="max-width:640px;margin:0 auto;padding:32px 20px"><div style="border:1px solid #225b38;border-radius:20px;overflow:hidden;background:#0d1611"><div style="padding:26px 30px;border-bottom:1px solid #225b38"><div style="color:#39ff88;font-size:12px;font-weight:700;letter-spacing:2px">IVANLLOPIS.NET</div><h1 style="margin:10px 0 8px;font-size:28px;color:#fff">{escape(title)}</h1><p style="margin:0;color:#a7b9ac;line-height:1.6">{escape(intro)}</p></div><div style="padding:28px 30px;line-height:1.65">{content}</div></div><p style="color:#789080;font-size:12px;text-align:center">IvanLlopis.net · Software · Cloud · AI</p></div></body></html>"""


def send_cv_request(body: CvRequest) -> None:
    api_key = os.getenv("RESEND_API_KEY", "")
    sender = os.getenv("CV_MAIL_FROM", "IvanLlopis.net <cv@ivanllopis.net>")
    recipient = os.getenv("CV_MAIL_TO", "")
    if not all((api_key, sender, recipient)):
        raise RuntimeError("CV email service is not configured")

    resend.api_key = api_key
    language = body.language if body.language in EMAIL_COPY else "en"
    copy = EMAIL_COPY[language]
    safe_name = escape(body.name)
    safe_email = escape(body.email)
    safe_phone = escape(body.phone or "-")
    safe_message = escape(body.message).replace("\n", "<br>")

    def card(title: str, intro: str, content: str) -> str:
        return (
            '<div style="background:#050b07;padding:32px;color:#effff3;font-family:Arial,sans-serif">'
            '<div style="max-width:640px;margin:auto;border:1px solid #1b6b3b;border-radius:18px;overflow:hidden;background:#0a1710">'
            '<div style="padding:28px;border-bottom:1px solid #1b6b3b">'
            '<div style="color:#39ff88;font-size:12px;letter-spacing:2px">IVANLLOPIS.NET</div>'
            f'<h1 style="margin:14px 0 8px">{title}</h1><p style="color:#a8b9ad">{intro}</p></div>'
            f'<div style="padding:28px">{content}</div></div></div>'
        )

    admin_content = (
        f'<p><b style="color:#39ff88">{copy[3]}</b><br>{safe_name}</p>'
        f'<p><b style="color:#39ff88">{copy[4]}</b><br>{safe_email}</p>'
        f'<p><b style="color:#39ff88">{copy[5]}</b><br>{safe_phone}</p>'
        f'<p><b style="color:#39ff88">{copy[6]}</b><br>{language}</p>'
        f'<p><b style="color:#39ff88">{copy[7]}</b></p>'
        f'<div style="border-left:3px solid #39ff88;padding:14px 18px;background:#061009">{safe_message}</div>'
    )
    receipt_content = (
        f"<h2>{copy[9]}</h2><p>{copy[10]}</p><p>{copy[11]}</p>"
        '<p style="margin-top:28px;color:#39ff88"><b>IvanLlopis.net</b></p>'
    )
    admin_params: resend.Emails.SendParams = {
        "from": sender,
        "to": [recipient],
        "subject": copy[0],
        "reply_to": body.email,
        "html": card(copy[1], copy[2], admin_content),
        "text": f"{copy[1]}\n\n{copy[3]}: {body.name}\n{copy[4]}: {body.email}\n{copy[5]}: {body.phone or '-'}\n{copy[6]}: {language}\n\n{copy[7]}:\n{body.message}\n",
    }
    receipt_params: resend.Emails.SendParams = {
        "from": sender,
        "to": [body.email],
        "subject": copy[8],
        "html": card(copy[9], copy[10], receipt_content),
        "text": f"{copy[9]}\n\n{copy[10]}\n\n{copy[11]}\n\nIvanLlopis.net\n",
    }
    try:
        resend.Emails.send(admin_params)
        resend.Emails.send(receipt_params)
    except ResendError as error:
        raise RuntimeError("The CV request could not be sent") from error


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
    except RuntimeError as error:
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
