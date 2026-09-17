import json
import os
from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

PRODUCTION_ORIGIN = "https://ivanllopis.net"
ORIGIN = PRODUCTION_ORIGIN

DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("es", "ca", "eu", "en", "fr", "uk", "it", "tr")
LANGUAGES = SUPPORTED_LANGUAGES

INDEXABLE_PAGES = ("", "/hobbies")
SEO_IMAGE = f"{PRODUCTION_ORIGIN}/static/images/ivan-hero-transparent.webp"

SEO_TEXT = {
    "es": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Portfolio profesional de Ivan Llopis sobre ingeniería de software, "
            "arquitectura cloud, Azure, .NET, Python e inteligencia artificial."
        ),
        "hobbies_title": "Aficiones de Ivan Llopis",
        "hobbies_description": ("Aficiones, intereses y actividades personales de Ivan Llopis."),
        "locale": "es_ES",
    },
    "ca": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Portafolis professional d'Ivan Llopis sobre enginyeria de programari, "
            "arquitectura cloud, Azure, .NET, Python i intel·ligència artificial."
        ),
        "hobbies_title": "Aficions d'Ivan Llopis",
        "hobbies_description": ("Aficions, interessos i activitats personals d'Ivan Llopis."),
        "locale": "ca_ES",
    },
    "eu": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Ivan Llopisen portfolio profesionala: software ingeniaritza, hodeiko "
            "arkitektura, Azure, .NET, Python eta adimen artifiziala."
        ),
        "hobbies_title": "Ivan Llopisen zaletasunak",
        "hobbies_description": ("Ivan Llopisen zaletasunak, interesak eta jarduera pertsonalak."),
        "locale": "eu_ES",
    },
    "en": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Ivan Llopis's professional portfolio covering software engineering, "
            "cloud architecture, Azure, .NET, Python and artificial intelligence."
        ),
        "hobbies_title": "Ivan Llopis's Hobbies",
        "hobbies_description": (
            "Discover Ivan Llopis's hobbies, interests and personal activities."
        ),
        "locale": "en_US",
    },
    "fr": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Portfolio professionnel d'Ivan Llopis consacré au génie logiciel, au "
            "cloud, à Azure, .NET, Python et à l'intelligence artificielle."
        ),
        "hobbies_title": "Loisirs d'Ivan Llopis",
        "hobbies_description": (
            "Découvrez les loisirs, centres d'intérêt et activités personnelles d'Ivan Llopis."
        ),
        "locale": "fr_FR",
    },
    "uk": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Професійне портфоліо Ivan Llopis: програмна інженерія, хмарна "
            "архітектура, Azure, .NET, Python і штучний інтелект."
        ),
        "hobbies_title": "Захоплення Ivan Llopis",
        "hobbies_description": ("Захоплення, інтереси та особисті заняття Ivan Llopis."),
        "locale": "uk_UA",
    },
    "it": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Portfolio professionale di Ivan Llopis su ingegneria del software, "
            "architettura cloud, Azure, .NET, Python e intelligenza artificiale."
        ),
        "hobbies_title": "Interessi di Ivan Llopis",
        "hobbies_description": (
            "Scopri gli hobby, gli interessi e le attività personali di Ivan Llopis."
        ),
        "locale": "it_IT",
    },
    "tr": {
        "home_title": "Ivan Llopis | Software Engineer Lead",
        "home_description": (
            "Ivan Llopis'in yazılım mühendisliği, bulut mimarisi, Azure, .NET, "
            "Python ve yapay zekâ odaklı profesyonel portföyü."
        ),
        "hobbies_title": "Ivan Llopis'in Hobileri",
        "hobbies_description": (
            "Ivan Llopis'in hobilerini, ilgi alanlarını ve kişisel etkinliklerini keşfedin."
        ),
        "locale": "tr_TR",
    },
}

router = APIRouter(include_in_schema=False)


def is_staging(request: Request) -> bool:
    environment = os.getenv("APP_ENV", "production").lower()
    return environment == "staging" or request.url.hostname == "staging.ivanllopis.net"


def page_data(path: str) -> tuple[str, str, str, str]:
    parts = [part for part in path.split("/") if part]
    language = parts[0] if parts and parts[0] in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    suffix = "/hobbies" if len(parts) > 1 and parts[1] == "hobbies" else ""
    page_key = "hobbies" if suffix else "home"
    text = SEO_TEXT[language]
    return (
        language,
        suffix,
        text[f"{page_key}_title"],
        text[f"{page_key}_description"],
    )


def seo_head(request: Request) -> str:
    language, suffix, title, description = page_data(request.url.path)
    canonical = f"{PRODUCTION_ORIGIN}/{language}{suffix}"
    robots = "noindex, nofollow, noarchive" if is_staging(request) else "index, follow"

    alternates = "\n".join(
        (f'<link rel="alternate" hreflang="{code}" href="{PRODUCTION_ORIGIN}/{code}{suffix}">')
        for code in SUPPORTED_LANGUAGES
    )
    alternates += (
        f'\n<link rel="alternate" hreflang="x-default" '
        f'href="{PRODUCTION_ORIGIN}/{DEFAULT_LANGUAGE}{suffix}">'
    )

    structured_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{PRODUCTION_ORIGIN}/#website",
                "url": f"{PRODUCTION_ORIGIN}/",
                "name": "IvanLlopis.net",
                "inLanguage": list(SUPPORTED_LANGUAGES),
            },
            {
                "@type": "Person",
                "@id": f"{PRODUCTION_ORIGIN}/#person",
                "name": "Ivan Llopis",
                "url": f"{PRODUCTION_ORIGIN}/",
                "image": SEO_IMAGE,
                "jobTitle": "Software Engineer Lead",
            },
        ],
    }
    json_ld = json.dumps(structured_data, ensure_ascii=False).replace("</", "<\\/")

    return "\n".join(
        [
            "<!-- SEO managed by seo.py -->",
            f"<title>{escape(title)}</title>",
            (f'<meta name="description" content="{escape(description, quote=True)}">'),
            f'<meta name="robots" content="{robots}">',
            f'<link rel="canonical" href="{canonical}">',
            alternates,
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="IvanLlopis.net">',
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
            (f'<meta property="og:description" content="{escape(description, quote=True)}">'),
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:image" content="{SEO_IMAGE}">',
            f'<meta property="og:locale" content="{SEO_TEXT[language]["locale"]}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
            (f'<meta name="twitter:description" content="{escape(description, quote=True)}">'),
            f'<meta name="twitter:image" content="{SEO_IMAGE}">',
            f'<script type="application/ld+json">{json_ld}</script>',
        ]
    )


class SeoMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if is_staging(request):
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"

        content_type = response.headers.get("content-type", "")
        if response.status_code != 200 or "text/html" not in content_type:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        html = body.decode("utf-8")
        lower_html = html.lower()
        head_end = lower_html.find("</head>")

        if head_end < 0:
            return Response(
                body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="text/html",
            )

        title_start = lower_html.find("<title")
        if 0 <= title_start < head_end:
            title_end = lower_html.find("</title>", title_start)
            if title_end >= 0:
                html = html[:title_start] + html[title_end + len("</title>") :]
                head_end = html.lower().find("</head>")

        html = html[:head_end] + seo_head(request) + "\n" + html[head_end:]
        headers = dict(response.headers)
        headers.pop("content-length", None)

        return Response(
            html,
            status_code=response.status_code,
            headers=headers,
            media_type="text/html",
        )


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request) -> PlainTextResponse:
    if is_staging(request):
        content = "User-agent: *\nDisallow: /\n"
    else:
        content = f"User-agent: *\nAllow: /\n\nSitemap: {PRODUCTION_ORIGIN}/sitemap.xml\n"
    return PlainTextResponse(content)


@router.get("/sitemap.xml")
def sitemap() -> Response:
    urls = "\n".join(
        f"  <url><loc>{PRODUCTION_ORIGIN}/{language}{suffix}</loc></url>"
        for language in SUPPORTED_LANGUAGES
        for suffix in INDEXABLE_PAGES
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    return Response(content, media_type="application/xml")


def configure_seo(app) -> None:
    app.add_middleware(SeoMiddleware)
    app.include_router(router)
